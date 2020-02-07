#!/bin/bash
# shellcheck disable=SC2046

# source common functions
. common.sh

# save current branch name
touch ../.env/{GITHUB_BRANCH,GITHUB_USER}
get_github_branch_current > ../.env/GITHUB_BRANCH
get_git_user_name > ../.env/GITHUB_USER

# encrypt secret keys
travis encrypt \
  AWS_SECRET_KEY_ENCRYPTED=$(cat ../.secret/aws/AWS_SECRET_KEY) \
  AWS_KEY_ID_ENCRYPTED=$(cat ../.secret/aws/AWS_KEY_ID) \
  DOCKER_HUB_PASSWORD_ENCRYPTED=$(cat ../.secret/docker/DOCKER_HUB_PASSWORD) \
  --add env.global \
  --override \
  --org