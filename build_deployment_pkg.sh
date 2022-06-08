#!/usr/bin/env bash

# constants
function_name=lambda

echo "[INFO] Packaging function ${function_name} and it's dependencies"

source venv/bin/activate

if [ -d "pkg" ]
then
  rm -r pkg
  mkdir pkg
else
  mkdir pkg
fi

if [ -d "deployment_pkg" ]
then
  rm -r deployment_pkg
  mkdir deployment_pkg
else
  mkdir deployment_pkg
fi

cd pkg

# install dependencies listed in function dependencies file
while read line; do
    if [[ -z "$line" ]]
    then
        dependencies_exist=false
        echo "No dependencies to install"
    else
        dependencies_exist=true
        echo "[INFO] Zipping pkg: $line"
        pip install ${line} --target .
    fi
done < ../${function_name}/dependencies.txt

# delete deployment pkg if it exits
if test -f ../deployment_pkg/${function_name}.zip; then
    rm ../deployment_pkg/${function_name}.zip
fi

zip -r9 ../deployment_pkg/${function_name}.zip .

cd ../

rm -r ./pkg/

cd lambda

# add function code py file to zip file
zip -g ../deployment_pkg/${function_name}.zip index.py

cd ..

## create zip file with all packages
#if [ test ${dependencies_exist} = true ]
#then
#  zip -r9 ../deployment_pkg/${function_name}.zip .
#
#  cd ../
#
#  rm -r ./pkg/
#
#  # add function code py file to zip file
#  zip -g deployment_pkg/${function_name}.zip ${function_name}/index.py
#
#else
#
#  cd ../
#
#  rm -r ./pkg/
#
#  # add function code py file to zip file
#  zip -r9 deployment_pkg/${function_name}.zip ${function_name}/index.py
#
#fi

# upload deployment pkg to s3 repo and update lambda database table
#python upload_lambda_function_to_repo.py ${function_name} ${repo_name}