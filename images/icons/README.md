## Adding new images

Requirements:
```shell
brew install librsvg rename
```

Process:
```shell
wget https://github.com/devicons/devicon/archive/refs/heads/master.zip
unzip master.zip
cat devicon-master/devicon.json | jq -e '.[] | select( .tags | index("programming") ) | .name' | jq -r | xargs -n 1 -I {} cp -f 'devicon-master/icons/{}/{}-original.svg' {}.svg
ls *.svg | xargs -n 1 -I {} rsvg-convert -h 128 {} -o {}.png
rename 's/.svg.png/.png/' *.svg.png
```
