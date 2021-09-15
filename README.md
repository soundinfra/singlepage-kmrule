# Single Web Page ([kmrule.com](https://kmrule.com))
This repository is an example of a single web page, powered by
[Sound//Infra](https://soundinfra.com).

[kmrule.com](https://kmrule.com) has some images, text, CSS, and even some
JavaScript to make it interactive. But the main thing that this repository shows
is just how easy it is to make changes to a web page that is powered by
**Sound//Infra**.

The web is made up of *resources*, each with
a [URL](https://en.wikipedia.org/wiki/URL), or web address,
like `https://kmrule.com/index.html`. When you click on a link in your browser,
you get taken to a URL.

This repository demonstrates two ways to add or update resources:

1. Using the command line.
2. Using the included Python script.

# Add or update a resource using the command line
To upload, or publish a resource to your domain, you just need to do a
HTTP `PUT` request. One way to do this is with the `curl` command, which is
installed on most systems:
```
me@host> SOUNDINFRA_TOKEN=[... your secret token ...]
me@host> curl -X PUT  \
 > -H "Authorization: Bearer $SOUNDINFRA_TOKEN" \
 > -H "Content-Type:" \
 > --data-binary "@public/index.html" \
 > https://kmrule.com/index.html
1ee1e6f4c99a61af0e718560785569cc,index.html
me@host>
```
A quick rundown of each part of the `curl` command above:

* `-X PUT` tells curl to send a HTTP `PUT` request, **Sound//Infra** also
  supports `DELETE` ([how to delete](#Deleting)).
* The `Authorization` header with your secret token is how **Sound//Infra**
  ensures that only you can make changes to your domain. Without your token, an
`Unauthorized` or `Forbidden` response
  will be returned. Just remember not to share your token with anybody else!
* Setting `Content-Type:` stops the `curl` command from using it's (incorrect)
  default content type. **Sound//Infra** will automatically guess the content
  type based on common file extensions (`.html` will be `text/html`). You could
  also specify `Content-Type: text/html`.
* `--data-binary` tells the `curl` command to upload the contents of the file
  `public/index.html`
* Last but not least is the URL `https://kmrule.com/index.html` where the
  file you uploaded will be published to the web.

The response `1ee1e6f4c99a61af0e718560785569cc,index.html` is the MD5 hash,
and path of your file.

### Check that your file was uploaded correctly
The first way to check that your file was uploaded correctly is to visit
[https://kmrule.com/index.html](https://kmrule.com/index.html) in your browser.
The path `index.html` is special, so you can also visit
[https://kmrule.com](https://kmrule.com).

The second way to check your file was uploaded correctly is to check hash of
your local file against what **Sound//Infra** returned. You can use the
`md5sum` `md5` or `openssl md5` commands ([how to use md5 commands](#Hashing)).

## See what is currently published to your domain
To check what is currently published to your domain, make a HTTP `OPTIONS`
request to your domain:
```
me@host> curl -X OPTIONS \
 > -H "Authorization: Bearer $SOUNDINFRA_TOKEN" \
 > https://kmrule.com
 5f25c9509a9add571f5c75f2b1b41e93,error.html
 904d7bfb6107e74ae0469d06009e1250,images/fig_01_The_Pyrmont_Pad-full.png
   ... more resources ...
   ... in alphabetical order ...
 1ee1e6f4c99a61af0e718560785569cc,index.html
me@host>
```
**Sound//Infra** will return the MD5 hash, and path of every resource on your
domain (in alphabetical order, up to 1000 files).

## Summary
Using simple HTTP requests the `curl` command, we were able to update,
and view the contents of `https://kmrule.com`.

With **Sound//Infra**:

* *You own your story*. Your resources are published to the web on *your
  domain*, so links to can continue to work forerver, even if you choose a
  different way to power your domain in the future.
* There's *no software to install or update*. **Sound//Infra** uses standards,
  simple mechanisms like HTTP. There's no need to install special software.
* *We do the configuration*. You can spend time perfecting your content and we
  take care of all the complicated configuration, like security protections, web
  servers, cloud services, and backups.

We are working on more ways to publish your documents, photos, and other content
to the web, so stay tuned, this is just the beginning!

## Footnotes
### Hashing
Works on Linux and some Macs:
```
me@host> md5sum public/index.html
1ee1e6f4c99a61af0e718560785569cc  public/index.html
```
Works on Macs:
```
me@host> md5 public/index.html
MD5 (public/index.html) = 1ee1e6f4c99a61af0e718560785569cc
```
Works if you have openssl installed:
```
me@host> openssl md5 public/index.html
MD5(public/index.html)= 1ee1e6f4c99a61af0e718560785569cc
```

### Deleting
You can delete resources with a HTTP `DELETE` request, like so:
```
me@host> curl -X DELETE -H "Authorization: Bearer $SOUNDINFRA_TOKEN" \
> https://kmrule.com/foo.html
me@host>
```
Note that this request succeeds *even if* the resource didn't exist in the
first place.

Also, it's worth pointing out that while it's easy to delete a resource with
**Sound//Infra**, once you publish something to the web, other people, and web
pages may link to that resource. So by deleting it, you may break those links.
Additionally, people, and machines, like search engines may download that
resource and save it forever. Think of the web as a place you want to publish
things that will be available *forever*.
