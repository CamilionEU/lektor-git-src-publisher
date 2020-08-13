#!/bin/sh -e

CUR_DIR="$(pwd)"
BASE_DIR="$(dirname "$(realpath "${0}")")"

# This sets up a basic lektor project that uses this plugin
extract_project() {
	cd "${1}"
	sh "${BASE_DIR}/minimal.shar"
	cd "${CUR_DIR}"
}

# This initialises the git environment to be used for testing.
setup_git_environment() {
	git_cmd="git -C ${1}"
	git_remote="${2}"
	if [ -z "${git_remote}" ]; then
		git_remote="${CUR_DIR}/${1}.git"
	fi
	# Start git repo
	${git_cmd} init
	# Setup committer
	${git_cmd} config user.name "Lektor Bot"
	${git_cmd} config user.email "bot@getlektor.com"
	# Add minimal project source
	${git_cmd} add .
	${git_cmd} commit -m "Initial commit."
	# Setup remote
	git init --bare "${git_remote}"
	${git_cmd} remote add remote "${git_remote}"
	# Bring remote/working dir together
	${git_cmd} checkout -b main
	${git_cmd} branch -D master
	${git_cmd} push --set-upstream remote main
}

# We add a spurious change so that the working dir is dirty
make_dirty_project() {
	cat >> "${1}/content/contents.lr" <<EOF

This text has been added to test the <pre>gitsrc-push://main</pre> publisher.
EOF
}

# Perform sanity checks and refuse running if necessary
GIT_BIN="$(which git)"
if [ -z "${GIT_BIN}" ] || [ ! -x "${GIT_BIN}" ]; then
	echo "Could not find the git binary in your system" >> /dev/stderr
	exit 1
fi
if [ -d "minimal" ] || [ -d "minimal.git" ] || \
	[ -d "nested" ] || [ -d "nested.git" ]; then
	echo "This would overwrite (minimal|nested)(|.git), not running." >> \
		/dev/stderr
	exit 1
fi

# Test case 1:
#   Setup a 'standard' project with .lektorproject in git root
extract_project "."
setup_git_environment "minimal"
make_dirty_project "minimal"

# Test case 2:
#   Setup a 'nested' project with .lektorproject deep in the git tree
mkdir -p "nested/project"
extract_project "nested/project"
setup_git_environment "nested"
make_dirty_project "nested/project/minimal"
