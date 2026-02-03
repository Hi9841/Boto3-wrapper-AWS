import boto3
import click
import sys
import os
import uuid
from botocore.exceptions import NoCredentialsError, ClientError

MAX_RESOURCES = 2

def get_global_count():
    ec2 = boto3.client('ec2')
    s3 = boto3.client('s3')

    filters = [
        {'Name': 'tag:CreatedBy', 'Values': ['Hi-platform-cli']},
        {'Name': 'instance-state-name', 'Values': ['running']}
    ]
    ec2_response = ec2.describe_instances(Filters=filters)
    ec2_count = sum(len(r['Instances']) for r in ec2_response['Reservations'])

    s3_response = s3.list_buckets()
    s3_count = 0
    if 'Buckets' in s3_response:
        for bucket in s3_response['Buckets']:
            if bucket['Name'].startswith("hi-platform-cli"):
                s3_count += 1
    
    return ec2_count + s3_count


@click.group()
def cli():
    pass

@cli.command()
def configure():
    access_key = click.prompt("AWS Access Key ID")
    secret_key = click.prompt("AWS Secret Access Key", hide_input=True)
    region = click.prompt("Default region name", default="us-east-1")
    
    aws_folder = os.path.expanduser("~/.aws")
    if not os.path.exists(aws_folder):
        os.makedirs(aws_folder)
    
    with open(os.path.join(aws_folder, "credentials"), "w") as f:
        f.write(f"[default]\naws_access_key_id = {access_key}\naws_secret_access_key = {secret_key}\n")
    
    with open(os.path.join(aws_folder, "config"), "w") as f:
        f.write(f"[default]\nregion = {region}\n")
    
    click.echo("Configuration saved successfully.")

@cli.group()
def ec2():
    pass

@ec2.command()
@click.option('--type', '-t', type=click.Choice(['t3.micro', 't2.small']), required=True)
@click.option('--os', '-o', type=click.Choice(['amazon-linux', 'ubuntu']), required=True)
def create(type, os):
    try:
        boto3.client('sts').get_caller_identity()
    except (NoCredentialsError, ClientError):
        click.echo("Error: Unable to connect to AWS.")
        click.echo("Please run 'python main.py configure' first.")
        sys.exit(1)

    click.echo("AWS Configuration verified. Checking global limits...")
    
    total_count = get_global_count()

    if total_count >= MAX_RESOURCES:
        click.echo(f"Error: Global Limit reached. You have {total_count} resources running.")
        sys.exit(1)

    ssm = boto3.client('ssm')
    if os == 'amazon-linux':
        param_name = '/aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64'
    else:
        param_name = '/aws/service/canonical/ubuntu/server/24.04/stable/current/amd64/hvm/ebs-gp3/ami-id'
    
    response = ssm.get_parameter(Name=param_name)
    ami_id = response['Parameter']['Value']
    ec2_client = boto3.client('ec2')

    click.echo(f"Limit OK ({total_count}/{MAX_RESOURCES}). Launching {os}...")    
    ec2_client.run_instances(
        ImageId=ami_id,
        InstanceType=type,
        MinCount=1,
        MaxCount=1,
        TagSpecifications=[
            {
                'ResourceType': 'instance',
                'Tags': [
                    {'Key': 'CreatedBy', 'Value': 'Hi-platform-cli'},
                    {'Key': 'Name', 'Value': f"Hi-platform-cli-{os}-node"}
                ]
            }
        ]
    )
    click.echo(f"Success! Launched {type} instance.")

@ec2.command()
@click.option('--start',is_flag=True, help="Start the instance")
@click.option('--stop',is_flag=True, help="Stop the instance")
@click.option('--instance-id', required=True, help="The Instance ID")
def manage(start,stop,instance_id):
    if start and stop:
        click.echo("Error: You cannot specify both --start and --stop.")
        sys.exit(1)
    
    if not start and not stop:
        click.echo("Error: You must specify --start or --stop.")
        sys.exit(1)

    ec2 = boto3.client('ec2')
    try:
        response = ec2.describe_instances(InstanceIds=[instance_id])
        tags = response['Reservations'][0]['Instances'][0].get('Tags', [])
        
        is_our_instance = False
        for tag in tags:
            if tag['Key'] == 'CreatedBy' and tag['Value'] == 'Hi-platform-cli':
                is_our_instance = True
                break
        
        if not is_our_instance:
            click.echo(f"Error: Instance {instance_id} was not created by this CLI. Access Denied.")
            sys.exit(1)

    except Exception:
        click.echo(f"Error: Instance {instance_id} not found.")
        sys.exit(1)

    instance = response['Reservations'][0]['Instances'][0]
    state = instance['State']['Name']

    if start:
        if state == 'running':
            click.echo(f"Aborted: Instance {instance_id} is already running.")
            sys.exit(0)
        if state == 'pending':
            click.echo(f"Aborted: Instance {instance_id} is already starting up (pending).")
            sys.exit(0)

        click.echo(f"Starting instance {instance_id}...")
        ec2.start_instances(InstanceIds=[instance_id])
    
    if stop:
        if state == 'stopped':
            click.echo(f"Aborted: Instance {instance_id} is already stopped.")
            sys.exit(0)
        if state == 'stopping':
            click.echo(f"Aborted: Instance {instance_id} is already shutting down.")
            sys.exit(0)
        if state == 'terminated':
             click.echo(f"Error: Instance {instance_id} is terminated and cannot be stopped.")
             sys.exit(1)

        click.echo(f"Stopping instance {instance_id}...")
        ec2.stop_instances(InstanceIds=[instance_id])
        
    click.echo(f"Success.")


@ec2.command()
def list():
    click.echo("Listing instances")
    
    ec2 = boto3.resource('ec2')
    
    instances = ec2.instances.filter(
        Filters=[{'Name': 'tag:CreatedBy', 'Values': ['Hi-platform-cli']},
                 {'Name': 'instance-state-name', 'Values': ['running']}
                 ]
    )

    count = 0
    for instance in instances:
        name = "Unknown"
        if instance.tags:
            for tag in instance.tags:
                if tag['Key'] == 'Name':
                    name = tag['Value']
                    break
        
        click.echo(f"ID: {instance.id} | Name: {name} | State: {instance.state['Name']}")
        count+=1
    print(f"{count} Instances running")


@cli.group()
def s3():
    pass

@s3.command()
@click.option('--pub', is_flag=True, help="Make bucket public")
@click.option('--pri', is_flag=True, help="Make bucket private (default)")
def create(pub, pri):
    if pub and pri:
        click.echo("Error: You cannot specify both --pub and --pri.")
        sys.exit(1)
        
    access_type = 'public' if pub else 'private'

    try:
        boto3.client('sts').get_caller_identity()
    except (NoCredentialsError, ClientError):
        click.echo("Error: Unable to connect to AWS.")
        click.echo("Please run 'python main.py configure' first.")
        sys.exit(1)

    click.echo("AWS Configuration verified. Checking global limits...")

    total_count = get_global_count()

    if total_count >= MAX_RESOURCES:
        click.echo(f"Error: Global Limit reached. You have {total_count} resources running.")
        sys.exit(1)        
    
    bucket_name = f"hi-platform-cli-storage-{str(uuid.uuid4())[:8]}"

    click.echo(f"Limit OK ({total_count+1}/{MAX_RESOURCES}). Creating {access_type} Bucket {bucket_name}...")    

    s3 = boto3.client('s3')
    
    s3.create_bucket(Bucket=bucket_name)

    s3.put_bucket_tagging(
        Bucket=bucket_name,
        Tagging={
            'TagSet': [
                {'Key': 'CreatedBy', 'Value': 'Hi-platform-cli'}, 
                {'Key': 'Name', 'Value': bucket_name}          
                ]
        }
    )    

    if pub:
        s3.delete_public_access_block(Bucket=bucket_name)
        
        s3.put_bucket_ownership_controls(
            Bucket=bucket_name,
            OwnershipControls={
                'Rules': [{'ObjectOwnership': 'BucketOwnerPreferred'}]
            }
        )
        
        s3.put_bucket_acl(Bucket=bucket_name, ACL='public-read')

    click.echo(f"Success! Created {access_type} Bucket.")


@s3.command()
@click.option('--bucket', required=True, help="The Bucket Name")
@click.option('--file', required=True, help="The file path to upload")
def upload(bucket , file):
    if not os.path.exists(file):
        click.echo(f"Error: The file '{file}' does not exist")
        sys.exit(1)

    s3 = boto3.client('s3')
    try:
        tags = s3.get_bucket_tagging(Bucket=bucket)
        tag_set = tags['TagSet']
        
        is_our_bucket = False
        for tag in tag_set:
            if tag['Key'] == 'CreatedBy' and tag['Value'] == 'Hi-platform-cli':
                is_our_bucket = True
                break
        
        if not is_our_bucket:
            click.echo(f"Error: Access Denied. Bucket '{bucket}' is not managed by Hi-platform-cli.")
            sys.exit(1)

        file_name = os.path.basename(file)
        s3.upload_file(file, bucket, file_name)
        click.echo("Success! File uploaded.")

    except ClientError as e:
        click.echo(f"Error: Unable to verify bucket tags. {e}")
        sys.exit(1)
    
    click.echo("Uploading Files...")


@s3.command()
def list():
    click.echo("Listing Buckets based on Tags...")
    
    s3 = boto3.client('s3')
    response = s3.list_buckets()
    
    count = 0
    if 'Buckets' in response:
        for bucket in response['Buckets']:
            bucket_name = bucket['Name']
            
            try:
                tags = s3.get_bucket_tagging(Bucket=bucket_name)
                tag_set = tags['TagSet']
                
                is_our_bucket = False
                for tag in tag_set:
                    if tag['Key'] == 'CreatedBy' and tag['Value'] == 'Hi-platform-cli':
                        is_our_bucket = True
                        break
                
                if is_our_bucket:
                    click.echo(f"Name: {bucket_name} | Created: {bucket['CreationDate']}")
                    count += 1

            except ClientError:
                continue

    click.echo(f"Found {count} Buckets.")

@cli.group()
def route53():
    pass

@route53.command()
def list():
    click.echo("Listing Route53...")

if __name__ == '__main__':
    cli()