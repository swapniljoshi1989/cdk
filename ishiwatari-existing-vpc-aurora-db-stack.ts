import * as cdk from 'aws-cdk-lib';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as rds from 'aws-cdk-lib/aws-rds';

import { Construct } from 'constructs';
import { ConfigEnvironment } from './config-environment';
// import * as sqs from 'aws-cdk-lib/aws-sqs';

export class ExistingVPCAuroraDBStack extends cdk.Stack {
    constructor(scope: Construct, id: string, props?: cdk.StackProps) {
        super(scope, id, props);
        
        const environment = this.node.tryGetContext('environment');
        if (!environment) {
            throw new Error('environment context is required');
        }
        

        const isProd = environment === 'prod';
        
        
        type Stage = keyof typeof ConfigEnvironment;
        const stage = this.node.tryGetContext('stage') as Stage;
        if (!stage) {
            throw new Error('stage is required');
        }
        
        const config = ConfigEnvironment[stage];

        if (!config) {
            throw new Error('The settings for the specified stage do not exist.');
        }
        
        const vpcId = config.vpcId;
        
        
        
        const auroraDBCluster = new rds.DatabaseCluster(this,'AuroraDBCluster',{
            engine: rds.DatabaseClusterEngine.auroraPostgres({
                version: rds.AuroraPostgresEngineVersion.VER_15_10,
            }),
            
            serverlessV2MaxCapacity: 4.0,
            serverlessV2MinCapacity: 0.5,
            
            writer: rds.ClusterInstance.serverlessV2("writer",{
                publiclyAccessible: false,
            }),
            
            readers: [
                rds.ClusterInstance.serverlessV2("reader1",{
                    publiclyAccessible: false,
                    scaleWithWriter: true,
                }),
            ],
            

            
            vpc: ec2.Vpc.fromLookup(this,'ImportedVPC',{
                vpcId: vpcId,
            }),
            
            storageEncrypted: true,
            deletionProtection: isProd,
            deleteAutomatedBackups: !isProd,
            removalPolicy: isProd ? cdk.RemovalPolicy.RETAIN : cdk.RemovalPolicy.DESTROY,
            vpcSubnets: {
                subnetType: ec2.SubnetType.PRIVATE_ISOLATED,
            },
            
            
        });
        
        
        new cdk.CfnOutput(this, 'ClusterEndpoint', {value: auroraDBCluster.clusterEndpoint.hostname});
        new cdk.CfnOutput(this, 'ReaderEndpoint', {value: auroraDBCluster.clusterReadEndpoint.hostname});
        
  }
}
