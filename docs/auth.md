In order to access private repositories hosted on a third-party platform like
GitHub or Bitbucket, cgitize needs to pass authentication on the hosting
server.  Authentication in Git is done either via HTTPS, or via SSH.

When using SSH, there're multiple methods to give cgitize access to SSH keys.

1. Use SSH keys (possibly passwordless) directly.  This is stupid, since it
   would require storing SSH keys and the passwords to them on the cgitize
   server.  Plus, I don't think either GitHub or Bitbucket support read-only
   SSH keys.

2. Give cgitize access to a ssh-agent.  This is less stupid, but would require
   a cumbersome setup.  The host ssh-agent can be used (including when cgitize
   is run in a Docker container), but in my experience, this is somewhat
   inconvenient (you have to add keys manually to the ssh-agent every time you
   reboot, etc.).

When using HTTPS, there're multiple options to access the private repositories.

1. Pass the account password in the URL.  Doesn't work with 2FA, incredibly
   insecure.

2. Use OAuth.  I thought this was too complicated to implement quickly.

3. Use per-application passwords.  This option is pretty cool.  Both GitHub (in
   the form of "personal access tokens") and Bitbucket (calls them "app
   passwords") support creating one-purpose passwords that are supposed to be
   used by a single app only.  They allow to bypass the 2FA also.  cgitize will
   support this option.
