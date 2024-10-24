#

## 1. How to update the forked repo

1.1. Update your local repo. Change to the 'master' branch and pull the commits from your remote **origin** (not from upstream):

```
$ cd wrs-config-generator
$ git branch
* gsi                       # you're in the 'gsi' branch
  master

$ git checkout master       # now in the 'master' branch
Switched to branch 'master'
Your branch is behind 'origin/master' by 4 commits, and can be fast-forwarded.
  (use "git pull" to update your local branch)

$ git pull                  # pull from origin
Updating f83b6fa..d557f78
...
```

Now your local repo is up-to-date.

1.2. Get the latest changes from **upstream** and merge it to your local repo

```
$ git fetch upstream         # fetch the latests changes from upstream
warning: redirecting to https://gitlab.cern.ch/white-rabbit/wrs-config-generator.git/
remote: Enumerating objects: 96, done.
remote: Counting objects: 100% (96/96), done.
remote: Compressing objects: 100% (95/95), done.
remote: Total 96 (delta 48), reused 0 (delta 0), pack-reused 0 (from 0)
Unpacking objects: 100% (96/96), 67.10 KiB | 2.16 MiB/s, done.
From https://gitlab.cern.ch/white-rabbit/wrs-config-generator
   d557f78..fb2abf6  master           -> upstream/master
 * [new branch]      orson-wrsw-7.0.0 -> upstream/orson-wrsw-7.0.0
   d557f78..f35e85c  proposed_master  -> upstream/proposed_master
 * [new tag]         w6.1.0_c1.0.0_r3 -> w6.1.0_c1.0.0_r3
 * [new tag]         w7.0.0_c1.0.0_r2 -> w7.0.0_c1.0.0_r2
 * [new tag]         w6.1.0_c1.0.0_r2 -> w6.1.0_c1.0.0_r2
 * [new tag]         w7.0.0_c1.0.0_r1 -> w7.0.0_c1.0.0_r1
```

All changes are not yet mirrored into the 'master' branch of your local repo. Let's do it with 'merge':

```
$ git merge upstream/master
Updating d557f78..fb2abf6
...
```

Once merge is complete, you can push everything to your remote **origin** repo.

3. Push the updated local repo to your remote **origin**:

```
$ git push
Enumerating objects: 109, done.
Counting objects: 100% (109/109), done.
Delta compression using up to 12 threads
Compressing objects: 100% (95/95), done.
Writing objects: 100% (96/96), 54.61 KiB | 7.80 MiB/s, done.
Total 96 (delta 58), reused 0 (delta 0), pack-reused 0
remote: Resolving deltas: 100% (58/58), completed with 12 local objects.
To https://github.com/GSI-CS-CO-Forks/wrs-config-generator
   d557f78..fb2abf6  master -> master
```
