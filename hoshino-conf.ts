import * as cdk from 'aws-cdk-lib';
	
	type Environment = 'dev' | 'prod';
	
export class ConfProps {
	
	az1: string = 'ap-northeast-3a';
	az2: string = 'ap-northeast-3b';
	privateCidr1: string = '172.31.48.0/20';
	privateCidr2: string = '172.31.64.0/20';
	vpcId: string = 'vpc-0d81efeeba9aa700c';
	
	removalPolicy: cdk.RemovalPolicy;
	backupRetentionDays: number;
	
	private constructor(removalPolicy: cdk.RemovalPolicy,backupRetentionDays: number){
		this.removalPolicy = removalPolicy;
		this.backupRetentionDays = backupRetentionDays;
	}
	
	static fromEnvironment(environment: Environment): ConfProps{
		if(environment === 'prod'){
			return new ConfProps(cdk.RemovalPolicy.RETAIN,7);
		}else if(environment === 'dev'){
			return new ConfProps(cdk.RemovalPolicy.DESTROY,3);
		}
		throw new Error('Type "-c stage=dev" or "stage = prod"');
	}
};

/*
export const az1: string = 'ap-northeast-3a';
export const az2: string = 'ap-northeast-3b';
export const removalPolicy : cdk.RemovalPolicy = cdk.RemovalPolicy.RETAIN;
export const backupRetentionDays : number = 7;
*/