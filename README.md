# How to update forked repository from CLI (command-line interface)

To update your fork with the upstream, get the remote to your local repository.
This allows you to fetch changes made in the original repository and push the changes to your local repository.

By default, local repository is not directly linked to the original repository.

```
$ git remote -v
origin	https://github.com/GSI-CS-CO-Forks/wrs-config-generator (fetch)
origin	https://github.com/GSI-CS-CO-Forks/wrs-config-generator (push)
```

It shows that original repository (the remote repository that you forked from) is not linked.
Link your repository with the original, upstream repository.

```
$ git remote add upstream https://gitlab.cern.ch/white-rabbit/wrs-config-generator.git
```

Now, check the remote repos

```
$ git remote -v
origin	https://github.com/GSI-CS-CO-Forks/wrs-config-generator (fetch)
origin	https://github.com/GSI-CS-CO-Forks/wrs-config-generator (push)
upstream	https://gitlab.cern.ch/white-rabbit/wrs-config-generator.git (fetch)
upstream	https://gitlab.cern.ch/white-rabbit/wrs-config-generator.git (push)
```

It's ready to fetch the changes/commits from the upstream

```
$ git fetch upstream
remote: Enumerating objects: 19, done.
remote: Counting objects: 100% (19/19), done.
remote: Compressing objects: 100% (16/16), done.
remote: Total 16 (delta 5), reused 4 (delta 0), pack-reused 0
Unpacking objects: 100% (16/16), 76.11 KiB | 490.00 KiB/s, done.
From https://gitlab.cern.ch/white-rabbit/wrs-config-generator
 * [new branch]      adam             -> upstream/adam
 * [new branch]      adam-git         -> upstream/adam-git
 * [new branch]      adam-vlans       -> upstream/adam-vlans
 * [new branch]      icalepcs-2017    -> upstream/icalepcs-2017
 * [new branch]      master           -> upstream/master
 * [new branch]      proposed_master  -> upstream/proposed_master
 * [new tag]         w6.0.0_c1.0.0_r7 -> w6.0.0_c1.0.0_r7
 * [new tag]         w6.0.1_c1.0.0_r2 -> w6.0.1_c1.0.0_r2
 * [new tag]         w6.0.1_c1.0.0_r1 -> w6.0.1_c1.0.0_r1
```

Fetched changes, commits and branches are needed to be merged to the head branch.
Before doing the merge, make sure you are updating this changes on your master (switch between upstream/master and origin/master branches).

```
$ git checkout upstream/master
Note: switching to 'upstream/master'.

You are in 'detached HEAD' state. You can look around, make experimental
changes and commit them, and you can discard any commits you make in this
state without impacting any branches by switching back to a branch.

If you want to create a new branch to retain commits you create, you may
do so (now or later) by using -c with the switch command. Example:

  git switch -c <new-branch-name>

Or undo this operation with:

  git switch -

Turn off this advice by setting config variable advice.detachedHead to false

HEAD is now a$ git checkout master
Previous HEAD position was b810fae Added config files for 6.0.1 and comma in the list of supported versions
Switched to branch 'master'
Your branch is up to date with 'origin/master'.t b810fae Added config files for 6.0.1 and comma in the list of supported versions
```

```
$ git checkout master
Previous HEAD position was b810fae Added config files for 6.0.1 and comma in the list of supported versions
Switched to branch 'master'
Your branch is up to date with 'origin/master'.
```

Once on the origin/master branch, merge it with the upstream.

```
$ git merge upstream/
```

Finally, push new commits to publish them to your remote repository.

```
$ git push
```
