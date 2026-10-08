import * as cdk from 'aws-cdk-lib';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as rds from 'aws-cdk-lib/aws-rds';
import * as logs from 'aws-cdk-lib/aws-logs';
import * as conf from './conf';
import { Construct } from 'constructs';

export class FirstTypescriptScenarioStack extends cdk.Stack {
	constructor(scope: Construct, id: string,confs: conf.ConfProps, props?: cdk.StackProps) {
		super(scope, id, props);
		
		const vpc = ec2.Vpc.fromLookup(this,'DefaultVpc',{ vpcId: confs.vpcId });
		
		const privateSubnet1 = new ec2.PrivateSubnet(this,'PrivateSubnet1',{
			availabilityZone: confs.az1,
			cidrBlock: confs.privateCidr1,
			vpcId: vpc.vpcId,
		});
		
		const privateSubnet2 = new ec2.PrivateSubnet(this,'PrivateSubnet2',{
			availabilityZone: confs.az2,
			cidrBlock: confs.privateCidr2,
			vpcId: vpc.vpcId,
		});
		
		const subnetGroup = new rds.SubnetGroup(this, 'PrivateSubnetGroup',{
			description: 'Private subnet group',
			vpc: vpc,
			vpcSubnets: { subnets: [privateSubnet1,privateSubnet2]},
			removalPolicy: confs.removalPolicy,
		});
		
		const cluster = new rds.DatabaseCluster(this,'DatabaseCluster',{
			engine: rds.DatabaseClusterEngine.auroraPostgres({
				// 15.8 is unavailable.
				version: rds.AuroraPostgresEngineVersion.VER_15_10,
				}),
			serverlessV2MaxCapacity: 4.0,	//The max capacity in free tier is 4.0
			serverlessV2MinCapacity: 0.5,
			readers: [
				rds.ClusterInstance.serverlessV2('Reader',{
					availabilityZone: confs.az1,
					publiclyAccessible: false,
					scaleWithWriter: true,
				}),
			],
			writer: rds.ClusterInstance.serverlessV2('Writer',{
				availabilityZone: confs.az2,
				publiclyAccessible: false,
			}),
			credentials: rds.Credentials.fromGeneratedSecret('dbadmin'),
			backup: { retention: cdk.Duration.days(confs.backupRetentionDays) },
			cloudwatchLogsRetention: logs.RetentionDays.ONE_MONTH,
			subnetGroup: subnetGroup,
			vpc: vpc,
			removalPolicy: confs.removalPolicy,
		});
		
		new cdk.CfnOutput(this,'clusterEndpointHostname',{ value: cluster.clusterEndpoint.hostname});
		new cdk.CfnOutput(this,'clusterEndpointPort',{ value: cluster.clusterEndpoint.port.toString()});
		new cdk.CfnOutput(this,'clusterEndpointSocketAddress',{ value: cluster.clusterEndpoint.socketAddress});
		new cdk.CfnOutput(this,'clusterReadEndpointHostname',{ value: cluster.clusterReadEndpoint.hostname});
		new cdk.CfnOutput(this,'clusterReadEndpointPort',{ value: cluster.clusterReadEndpoint.port.toString()});
		new cdk.CfnOutput(this,'clusterReadEndpointSocketAddress',{ value: cluster.clusterReadEndpoint.socketAddress});
	}
}