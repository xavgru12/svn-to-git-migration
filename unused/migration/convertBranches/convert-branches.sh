for t in `git branch -r | sed s_origin/__` ; do
 git branch $t origin/$t
 git branch -D -r origin/$t
done