#!/bin/bash -e
# shellcheck disable=SC2046
# shellcheck disable=SC2199
# shellcheck disable=SC2124
# shellcheck disable=SC2086

# source common functions
. task/common.sh

echo "[INFO] Executing Travis CI Wrapper"

TASK="PROD"
MSG="Update Travis secrets"
if [ "$#" -gt 0 ]; then
  if [[ "$@" == "TASK"* ]]; then
    shift
    TASK="$1"
    shift
    if [[ -n "$@" ]]; then
      MSG="$@"
    fi
  else
    MSG="$@"
  fi
fi

echo "[INFO] Arg inputs:"
echo "     | TASK: $TASK"
echo "     | GIT MSG : $MSG"

# save current branch name
touch .envfiles/{GITHUB_BRANCH,GITHUB_USER}
get_github_branch_current >.envfiles/GITHUB_BRANCH
get_git_user_name >.envfiles/GITHUB_USER

TEMPLATE_TRAVIS_BASE_YML=task/travis/template/.travis.base.yml
TEMPLATE_TRAVIS_AWS_YML=task/aws/template/.travis.aws.yml
TRAVIS_YML=.travis.yml

echo "[INFO] Get $TRAVIS_YML from templates for TASK:"
if [[ "$TASK" == "AWS" ]]; then
  echo "     | AWS"
  if [ -f $TRAVIS_YML ]; then
    echo "[INFO] Remove old Travis YML : $TRAVIS_YML"
    rm $TRAVIS_YML
  fi

  TRAVIS_TEMPLATES="
      $TEMPLATE_TRAVIS_BASE_YML
      $TEMPLATE_TRAVIS_AWS_YML
  "

else
  TRAVIS_TEMPLATES="
      $TEMPLATE_TRAVIS_BASE_YML
  "
fi

if [ -f $TRAVIS_YML ]; then
  echo "[INFO] Remove old Travis YML : $TRAVIS_YML"
  rm $TRAVIS_YML
fi

echo "[INFO] Concat Travis YML templates ($TRAVIS_TEMPLATES) and copy as $TRAVIS_YML"
$CWD/scripts/template_concat.py \
  "$TRAVIS_YML" \
  $TRAVIS_TEMPLATES

echo "[INFO] Get secrets for TASK:"
SECRETS="
  DOCKER_HUB_PASSWORD=$(cat .secretfiles/docker/DOCKER_HUB_PASSWORD)
  DOCKER_HUB_ID=$(cat .envfiles/DOCKER_HUB_ID)
  GITHUB_BRANCH=$(cat .envfiles/GITHUB_BRANCH)
  GITHUB_USER=$(cat .envfiles/GITHUB_USER)
  BUILD_TYPE=prod
"
AWS_SECRETS="
  AWS_SECRET_KEY=$(cat .secretfiles/aws/AWS_SECRET_KEY)
  AWS_KEY_ID=$(cat .secretfiles/aws/AWS_KEY_ID)
"

if [[ "$TASK" == "AWS" ]]; then
  echo "     | $TASK"
  SECRETS="$SECRETS $AWS_SECRETS"
fi

echo "[INFO] Trevis encrypt secrets: ($SECRETS)"
travis encrypt \
  $SECRETS \
  --add env.global \
  --override \
  --org

echo "[INFO] Execute TASK:"
if [[ "$TASK" == "AWS" ]]; then
  echo "     | $TASK"
  ./prod_aws UPLOAD_ENV

elif [[ "$TASK" == "K8S" ]]; then
  echo "     | K8S"
  ./prod_k8s

elif [[ "$TASK" == "PROD" ]]; then
  echo "     | PROD"
  echo "[INFO] Nothing todo."

else
  echo "[ERROR] Wrong task name : $TASK"
  exit 1
fi

git add -A
git commit -m "$MSG"
git push origin $(get_github_branch_current)
