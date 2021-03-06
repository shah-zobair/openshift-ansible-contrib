#!/usr/bin/env python
# vim: sw=2 ts=2

import click
import os
import sys

@click.command()

### Cluster options
@click.option('--console-port', default='8443', type=click.IntRange(1,65535), help='OpenShift web console port',
              show_default=True)
@click.option('--deployment-type', default='openshift-enterprise', help='OpenShift deployment type',
              show_default=True)

### AWS/EC2 options
@click.option('--region', default='us-east-1', help='ec2 region',
              show_default=True)
@click.option('--ami', default='ami-10251c7a', help='ec2 ami',
              show_default=True)
@click.option('--master-instance-type', default='m4.large', help='ec2 instance type',
              show_default=True)
@click.option('--node-instance-type', default='m4.large', help='ec2 instance type',
              show_default=True)
@click.option('--keypair', help='ec2 keypair name',
              show_default=True)
@click.option('--create-key', default='no', help='Create SSH keypair',
              show_default=True)
@click.option('--key-path', default='/dev/null', help='Path to SSH public key. Default is /dev/null which will skip the step',
              show_default=True)
@click.option('--create-vpc', default='yes', help='Create VPC',
              show_default=True)
@click.option('--vpc-id', help='Specify an already existing VPC',
              show_default=True)
@click.option('--private-subnet-id1', help='Specify a Private subnet within the existing VPC',
              show_default=True)
@click.option('--private-subnet-id2', help='Specify a Private subnet within the existing VPC',
              show_default=True)
@click.option('--private-subnet-id3', help='Specify a Private subnet within the existing VPC',
              show_default=True)
@click.option('--public-subnet-id1', help='Specify a Public subnet within the existing VPC',
              show_default=True)
@click.option('--public-subnet-id2', help='Specify a Public subnet within the existing VPC',
              show_default=True)
@click.option('--public-subnet-id3', help='Specify a Public subnet within the existing VPC',
              show_default=True)

### DNS options
@click.option('--public-hosted-zone', help='hosted zone for accessing the environment')
@click.option('--app-dns-prefix', default='apps', help='application dns prefix',
              show_default=True)

### Subscription and Software options
@click.option('--rhsm-user', help='Red Hat Subscription Management User')
@click.option('--rhsm-password', help='Red Hat Subscription Management Password',
                hide_input=True,)

### Miscellaneous options
@click.option('--byo-bastion', default='no', help='skip bastion install when one exists within the cloud provider',
              show_default=True)
@click.option('--no-confirm', is_flag=True,
              help='Skip confirmation prompt')
@click.help_option('--help', '-h')
@click.option('-v', '--verbose', count=True)

def launch_refarch_env(region=None,
                    ami=None,
                    no_confirm=False,
                    master_instance_type=None,
                    node_instance_type=None,
                    keypair=None,
                    create_key=None,
                    key_path=None,
                    create_vpc=None,
                    vpc_id=None,
                    private_subnet_id1=None,
                    private_subnet_id2=None,
                    private_subnet_id3=None,
                    public_subnet_id1=None,
                    public_subnet_id2=None,
                    public_subnet_id3=None,
                    byo_bastion=None,
                    public_hosted_zone=None,
                    app_dns_prefix=None,
                    deployment_type=None,
                    console_port=8443,
                    rhsm_user=None,
                    rhsm_password=None,
                    verbose=0):

  # Need to prompt for the R53 zone:
  if public_hosted_zone is None:
    public_hosted_zone = click.prompt('Hosted DNS zone for accessing the environment')

  # Create ssh key pair in AWS if none is specified
  if create_key in 'yes' and key_path in 'no':
    key_path = click.prompt('Specify path for ssh public key')
    keypair = click.prompt('Specify a name for the keypair')

 # If no keypair is not specified fail:
  if keypair is None and create_key in 'no':
    click.echo('A SSH keypair must be specified or created')
    sys.exit(1)

 # Name the keypair if a path is defined
  if keypair is None and create_key in 'yes':
    keypair = click.prompt('Specify a name for the keypair')

 # If no subnets are defined prompt:
  if create_vpc in 'no' and vpc_id is None:
    vpc_id = click.prompt('Specify the VPC ID')

 # If no subnets are defined prompt:
  if create_vpc in 'no' and private_subnet_id1 is None:
    private_subnet_id1 = click.prompt('Specify the first Private subnet within the existing VPC')
    private_subnet_id2 = click.prompt('Specify the second Private subnet within the existing VPC')
    private_subnet_id3 = click.prompt('Specify the third Private subnet within the existing VPC')
    public_subnet_id1 = click.prompt('Specify the first Public subnet within the existing VPC')
    public_subnet_id2 = click.prompt('Specify the second Public subnet within the existing VPC')
    public_subnet_id3 = click.prompt('Specify the third Public subnet within the existing VPC')

  # If the user already provided values, don't bother asking again
  if rhsm_user is None:
    rhsm_user = click.prompt("RHSM username?")
  if rhsm_password is None:
    rhsm_password = click.prompt("RHSM password?", hide_input=True, confirmation_prompt=True)

  # Calculate various DNS values
  wildcard_zone="%s.%s" % (app_dns_prefix, public_hosted_zone)

  # Display information to the user about their choices
  click.echo('Configured values:')
  click.echo('\tami: %s' % ami)
  click.echo('\tregion: %s' % region)
  click.echo('\tmaster_instance_type: %s' % master_instance_type)
  click.echo('\tnode_instance_type: %s' % node_instance_type)
  click.echo('\tkeypair: %s' % keypair)
  click.echo('\tcreate_key: %s' % create_key)
  click.echo('\tkey_path: %s' % key_path)
  click.echo('\tcreate_vpc: %s' % create_vpc)
  click.echo('\tvpc_id: %s' % vpc_id)
  click.echo('\tprivate_subnet_id1: %s' % private_subnet_id1)
  click.echo('\tprivate_subnet_id2: %s' % private_subnet_id2)
  click.echo('\tprivate_subnet_id3: %s' % private_subnet_id3)
  click.echo('\tpublic_subnet_id1: %s' % public_subnet_id1)
  click.echo('\tpublic_subnet_id2: %s' % public_subnet_id2)
  click.echo('\tpublic_subnet_id3: %s' % public_subnet_id3)
  click.echo('\tbyo_bastion: %s' % byo_bastion)
  click.echo('\tconsole port: %s' % console_port)
  click.echo('\tdeployment_type: %s' % deployment_type)
  click.echo('\tpublic_hosted_zone: %s' % public_hosted_zone)
  click.echo('\tapp_dns_prefix: %s' % app_dns_prefix)
  click.echo('\tapps_dns: %s' % wildcard_zone)
  click.echo('\trhsm_user: %s' % rhsm_user)
  click.echo('\trhsm_password: *******')
  click.echo("")

  if not no_confirm:
    click.confirm('Continue using these values?', abort=True)

  playbooks = ['playbooks/infrastructure.yaml', 'playbooks/openshift-install.yaml']

  for playbook in playbooks:

    # hide cache output unless in verbose mode
    devnull='> /dev/null'

    if verbose > 0:
      devnull=''

    # refresh the inventory cache to prevent stale hosts from
    # interferring with re-running
    command='inventory/aws/hosts/ec2.py --refresh-cache %s' % (devnull)
    os.system(command)

    # remove any cached facts to prevent stale data during a re-run
    command='rm -rf .ansible/cached_facts'
    os.system(command)

    command='ansible-playbook -i inventory/aws/hosts -e \'region=%s \
    ami=%s \
    keypair=%s \
    create_key=%s \
    key_path=%s \
    create_vpc=%s \
    vpc_id=%s \
    private_subnet_id1=%s \
    private_subnet_id2=%s \
    private_subnet_id3=%s \
    public_subnet_id1=%s \
    public_subnet_id2=%s \
    public_subnet_id3=%s \
    byo_bastion=%s \
    master_instance_type=%s \
    node_instance_type=%s \
    public_hosted_zone=%s \
    wildcard_zone=%s \
    console_port=%s \
    deployment_type=%s \
    rhsm_user=%s \
    rhsm_password=%s \' %s' % (region,
                    ami,
                    keypair,
                    create_key,
                    key_path,
                    create_vpc,
                    vpc_id,
                    private_subnet_id1,
                    private_subnet_id2,
                    private_subnet_id3,
                    public_subnet_id1,
                    public_subnet_id2,
                    public_subnet_id3,
                    byo_bastion,
                    master_instance_type,
                    node_instance_type,
                    public_hosted_zone,
                    wildcard_zone,
                    console_port,
                    deployment_type,
                    rhsm_user,
                    rhsm_password,
                    playbook)

    if verbose > 0:
      command += " -" + "".join(['v']*verbose)
      click.echo('We are running: %s' % command)

    status = os.system(command)
    if os.WIFEXITED(status) and os.WEXITSTATUS(status) != 0:
      return os.WEXITSTATUS(status)

if __name__ == '__main__':
  # check for AWS access info
  if os.getenv('AWS_ACCESS_KEY_ID') is None or os.getenv('AWS_SECRET_ACCESS_KEY') is None:
    print 'AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY **MUST** be exported as environment variables.'
    sys.exit(1)

  launch_refarch_env(auto_envvar_prefix='OSE_REFArch')
