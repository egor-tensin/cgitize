IFS= read -r -s -p 'Bitbucket token: ' CGITIZE_BITBUCKET_TOKEN
echo
IFS= read -r -s -p 'GitHub token: ' CGITIZE_GITHUB_TOKEN
echo
IFS= read -r -s -p 'GitLab token: ' CGITIZE_GITLAB_TOKEN
echo

export CGITIZE_BITBUCKET_USERNAME=cgitize-test
export CGITIZE_BITBUCKET_TOKEN
export CGITIZE_GITHUB_USERNAME=cgitize-test
export CGITIZE_GITHUB_TOKEN
export CGITIZE_GITLAB_USERNAME=cgitize-test
export CGITIZE_GITLAB_TOKEN
