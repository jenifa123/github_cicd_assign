import boto3
import pandas as pd

s3_client = boto3.client('s3')
sns_client = boto3.client('sns')
sns_arn = 'arn:aws:sns:ap-south-1:254241970276:send-notification-on-file-arrival'
output_file_name = '2024-03-09-output.json'

def lambda_handler(event, context):
    # TODO implement
    print(event)
    try:
        
        #Read JSON file from S3
        bucket_name = event["Records"][0]["s3"]["bucket"]["name"]
        s3_file_key = event["Records"][0]["s3"]["object"]["key"]
        print(bucket_name)
        print(s3_file_key)
        resp = s3_client.get_object(Bucket=bucket_name, Key=s3_file_key)
        print(resp['Body'])
        data =  resp['Body'].read().decode('utf-8')
        df_s3_data = pd.read_json(data)
        print('File read successfully')
        
        df_filtered_data = df_s3_data[df_s3_data['status']=='delivered']
                
        #write data to json
        
        df_filtered_json_data =  df_filtered_data.to_json(output_file_name,orient='records')
        
        #upload json file to target bucket
        
        s3_client.put_object(Bucket='doordash-target-zonee' ,Key=output_file_name,Body=df_filtered_json_data)

        message = "Input S3 File {} has been processed succesfuly with order status as Delivered !!".format("s3://"+bucket_name+"/"+s3_file_key)
        response = sns_client.publish(Subject="Daily Data Processing and Filtering successful",TargetArn=sns_arn, Message=message, MessageStructure='text')
    except Exception as err:
        print(err)
        message = "Input S3 File {} processing is Failed as there were no order status as Delivered !!".format("s3://"+bucket_name+"/"+s3_file_key)
        response = sns_client.publish(Subject="Daily Data Processing and Filtering Failed", TargetArn=sns_arn, Message=message, MessageStructure='text')