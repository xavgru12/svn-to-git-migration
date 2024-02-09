for t in `git branch -a | grep 'tags/' | sed s_remotes/origin/tags/__` ; do
 git tag $t origin/tags/$t
 git branch -d -r origin/tags/$t
done