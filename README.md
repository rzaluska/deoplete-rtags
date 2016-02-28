# deoplete-rtags

Use [deoplete.nvim](https://github.com/Shougo/deoplete.nvim) asynchronous
autocompletion together with [rtags](https://github.com/Andersbakken/rtags)
symbols database.

### Current project status:
**Proof of concept** :boom:

## recomended setup
- Make sure your project is [CMake](https://github.com/Kitware/CMake) driven
- Install [deoplete.nvim](https://github.com/Shougo/deoplete.nvim)
- Install this plugin
- Install [rtags](https://github.com/Andersbakken/rtags)
- Create CMake compilation database
```
mkdir your/build/directory
cd your/build/directory
cmake -DCMAKE_EXPORT_COMPILE_COMMANDS=ON your/project/root
```
- Run rtags server in separate terminal
```
rdm
```
- Run rtags client and ask server to use provided compilation database (this
will allow you to use completions based on files in your project and all
libraries mentioned in CMakeLists.txt)

    -J flag will tell rtags server to load compile_commands.json from provided
directory
```
rc -J your/build/directory
```
- You are ready to go just open file in your project and start typing.
Sugesstions will pop up automatically thanks to
[deoplete.nvim](https://github.com/Shougo/deoplete.nvim).

## related plugins
[vim-rtags](https://github.com/lyuts/vim-rtags) - you can use this plugin to
browse your codebase using rtags
