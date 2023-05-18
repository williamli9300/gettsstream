for %%i in (?.ts) do ren %%i 000%%i
for %%i in (??.ts) do ren %%i 00%%i
for %%i in (???.ts) do ren %%i 0%%i
copy /b ????.ts output.ts