import boto3
import uuid
from typing import Optional
from config.settings import (
    AWS_ACCESS_KEY_ID,
    AWS_SECRET_ACCESS_KEY,
    AWS_REGION,
    S3_BUCKET_NAME,
)


class S3Storage:
    """Handles cloud storage operations with AWS S3."""
    
    def __init__(self):
        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=AWS_REGION,
        )
        self.bucket_name = S3_BUCKET_NAME
    
    def upload_image(
        self,
        file_content: bytes,
        patient_id: str,
        filename_prefix: str = "original"
    ) -> str:
        """
        Upload image to S3.
        
        Args:
            file_content: Image binary content
            patient_id: Patient ID for organization
            filename_prefix: Prefix for the S3 key
        
        Returns:
            S3 key (path) of uploaded image
        """
        unique_id = str(uuid.uuid4())
        s3_key = f"images/{patient_id}/{filename_prefix}_{unique_id}.jpg"
        
        try:
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=file_content,
                ContentType="image/jpeg",
            )
            return s3_key
        except Exception as e:
            raise Exception(f"Failed to upload image to S3: {str(e)}")
    
    def upload_heatmap(
        self,
        heatmap_content: bytes,
        patient_id: str,
        scan_id: str
    ) -> str:
        """Upload Grad-CAM heatmap to S3."""
        s3_key = f"heatmaps/{patient_id}/heatmap_{scan_id}.jpg"
        
        try:
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=heatmap_content,
                ContentType="image/jpeg",
            )
            return s3_key
        except Exception as e:
            raise Exception(f"Failed to upload heatmap to S3: {str(e)}")
    
    def get_presigned_url(self, s3_key: str, expiration: int = 3600) -> str:
        """
        Generate a presigned URL for accessing the image.
        
        Args:
            s3_key: S3 key (path)
            expiration: URL expiration time in seconds (default 1 hour)
        
        Returns:
            Presigned URL
        """
        try:
            url = self.s3_client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket_name, "Key": s3_key},
                ExpiresIn=expiration,
            )
            return url
        except Exception as e:
            raise Exception(f"Failed to generate presigned URL: {str(e)}")
    
    def download_image(self, s3_key: str) -> bytes:
        """Download image from S3."""
        try:
            response = self.s3_client.get_object(
                Bucket=self.bucket_name,
                Key=s3_key
            )
            return response["Body"].read()
        except Exception as e:
            raise Exception(f"Failed to download image from S3: {str(e)}")
