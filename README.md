Convert an Obsidian directory vault to a Github Pages site by following directory structuring rules.
### Obsidian Vault Structuring Rules
##### 1. Structure rule: The existence of `README.md` file makes the directory valid to host on the site.
##### 2. Structure rule: __The graphics directory exception__.  Directories exactly named "graphics" are exempt from having a `README`. These graphics directorys contain supporting media. 
For example purposes, here is the entirity of my notes
```shell
$ tree my_obsidian_vault
.
├── about.md
├── graphics
│   ├── img1.png
│   └── motion.gif
├── home.md
├── physics
│   ├── golden_file.md
│   └── README.md
├── poetry
│   ├── poet
│   │   ├── README.md
│   │   └── scared to show this.md
│   └── showtime.md
└── README.md
```
_Home pages_ (`README.md`) are a directorys landing page. Home/landing page content are link(s) to the other possible directory home pages and/or other files. For example, below is the `tree` command ran inside an Obsidian vault.
#### All directories have their own `README.md` which acts as that directories' _Home Page_
In the example above, the landing page from the directory structure would yield:
- the content in the `README.md` (top level)
- a link to the web pages `home` and `about`
- a link to the web landing page of `physics`
- NOT a link to `poetry` because no `README.md`
#### The Recursive Creation of Web Pages from Parsing Rules
_recursively go through the obsidian file structure and parse markdown into html_
- Markdown files are converted to HTML using a minimal parser and written next to the originals.
When iterating through the lines of an Obsidian markdown files I will encounter traditional and Obsidian specific markdown artifacts. All markdown files will have a title/name. 
# Parsing Rules
## Things that happen at the beginning of the line
- ##### Multi-line Code Block
Has the a copy copy button
- ##### Title headings
The number of '#' will correspond to heading tag number. Bold, italic, and code formatting are all allowed in titles. 
- ##### Regular lines
paragraph tags
- ##### Web Hosted Images
Where the `250` is just the width and scales with original aspect ration, but height and width can be specified when `NxN` notation is used for `heightxwidth`. The `x` in the middle is lower case. 
```obsidian-markdown
![250](https://publish-01.obsidian.md/access/f786db9fac45774fa4f0d8112e232d67/Attachments/Engelbart.jpg)
```
- ##### Local Images
```obsidian-markdown
![[graphics/Engelbart.jpg]]
![[graphics/Engelbart.jpg|145]]
![[graphics/Engelbart.jpg|100x145]]
```
## Things that happen anywhere in the line
- ##### Bold text
- ##### External web link
### Usage
##### Run the markdown to html parser by pointing it at the root of your vault:
```bash
$ python -m obsidianvault_2_web.main /Users/gramjos/Documents/try_hosting_Vault
```
Outputs a directory called `try_hosting_Vault_ready_2_serve`
```shell
$ tree try_hosting_Vault_ready_2_serve 
try_hosting_Vault_ready_2_serve
├── about.html
├── about.md
├── graphics
│   └── img1.png
├── homie.html
├── homie.md
├── physics
│   ├── golden_file.html
│   ├── golden_file.md
│   ├── README.html
│   └── README.md
├── README.html
└── README.md

3 directories, 11 files
```
Given a directory like `try_hosting_Vault_raeady_2_serve` the `build.py` program creates the site. Note, `build.py` can handle any size directory as long as the structuring rules are followed. 
```shell
$ python build.py try_hosting_Vault_ready_2_serve 
```
`build.py` with output `HTML`, `Javascript`, and `CSS` files. This comprises a Single Page Web Application that can be host push right to Github to be hosted