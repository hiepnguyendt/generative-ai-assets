import boto3
import os
import json
from PIL import Image, ImageDraw
import base64
import io
from random import randint

INPUT_BUCKET = os.environ.get('INPUT_BUCKET')
IMAGE_PREFIX = os.environ.get('IMAGE_PREFIX')
GENERATED_IMAGE_PREFIX = os.environ.get('GENERATED_IMAGE_PREFIX')
BEDROCK_MODEL_ID = os.environ.get('BEDROCK_MODEL_ID')
REGION = os.environ.get('AWS_REGION')

s3_client = boto3.client('s3')
bedrock_client = boto3.client(service_name='bedrock-runtime', region_name=REGION)
rekognition_client =  boto3.client('rekognition')


def lambda_handler(event, context):

    request_payload = json.loads(event['body'])
    print(request_payload)
    
    #Fetch request payload
    image_file_name = request_payload['ImageFileName']
    image_file_format = image_file_name.split('.')[1]
    
    image_file_uri = f"s3://{INPUT_BUCKET}/{IMAGE_PREFIX}/{image_file_name}"
    
    # Path to store images files in temporary storage
    tmp_image_path = f'/tmp/{image_file_name}'
    tmp_output_path = f'/tmp/generated_{image_file_name}'

    try:
        
        s3_client.download_file(INPUT_BUCKET, f'{IMAGE_PREFIX}/{image_file_name}', tmp_image_path)    
        
        # Fetch the labels details from request
        labels = request_payload['Labels']

        # Generate image
        generate_image(tmp_image_path, tmp_output_path,  request_payload)
        
        #upload image
        s3_client.upload_file(tmp_output_path, INPUT_BUCKET, f'{GENERATED_IMAGE_PREFIX}/generated_{image_file_name}')
        
        results = {
            "ImageS3Key": f'{GENERATED_IMAGE_PREFIX}/generated_{image_file_name}'
        }
        
        print(results)
        
        return {
            'StatusCode': 200,
            'Body': {
                'Results': results
            }
        }
        
        
        
    except Exception as e:
        print('Error in generating image')
        print(e)
        return {
            'StatusCode': 500,
            'Body': {
                'Message': f'Error in gnerating image: {e}'
            }
        }        
        
    
    finally:
        if os.path.exists(tmp_image_path):
            os.remove(tmp_image_path)
        if os.path.exists(tmp_output_path):
            os.remove(tmp_output_path)



def invoke_endpoint(json):
    print(f"Request: {json}")
    response = bedrock_client.invoke_model(body=json, modelId=BEDROCK_MODEL_ID)
    return response

def nearest_multiple_of_64(dim):
    return (dim // 64) * 64

def image_to_base64(img_path) -> str:
    with open(img_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

# Add code here

    
    
    
    
    
     
    
    

