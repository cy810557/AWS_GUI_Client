#!/bin/bash
declare aws='aws --endpoint-url=http://10.5.41.14:7480 --profile test'

function upload(){
    # Usage 1: aws_upload /data/local_file_path/  # upload file/folder to Field_Test_Data/<date>
    # Usage 2: aws_upload /data/local_file_path/ /my_test_aws_folder/sub_folder  # upload file/folder to specified path
    declare local_path=$1
    declare bucket_name=$2
    declare target_path=$3
    if [[ ${target_path: -1} == "/" ]];then
        target_path=${target_path: 0:-1}
    fi
    ${aws} s3 cp $local_path s3://${bucket_name}/$target_path/`basename $local_path` --recursive
}

upload $1 $2 $3

