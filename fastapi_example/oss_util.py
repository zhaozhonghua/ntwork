import oss2

import setting


class AliyunOssUtil:

    @staticmethod
    def bucket(is_internal=False):
        if is_internal:
            endpoint = setting.oss_public_bucket['endpoint_internal']
            is_cname = False
        else:
            endpoint = setting.oss_public_bucket['endpoint']
            is_cname = False if not endpoint or ".aliyuncs.com" in endpoint else True
        auth = oss2.Auth(setting.oss_public_bucket['access_key_id'], setting.oss_public_bucket['access_key_secret'])
        bucket = oss2.Bucket(auth, endpoint, setting.oss_public_bucket['bucket_name'], is_cname=is_cname)
        return bucket

    @staticmethod
    def put_object_from_file(local_file, oss_key, is_internal=False):
        AliyunOssUtil.bucket(is_internal=is_internal).put_object_from_file(oss_key, local_file)
        return f"{setting.oss_public_bucket}/{oss_key}"
