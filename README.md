How to run the code
On the first FPGA, open the pokemon_game.ipynb file in JupyterNotebook of the FPGA and make sure both pg_block_sprite_t35.bit and pg_block_sprite_t35.hwh are in the same directory.
Make sure all the needed libraries are installed (ex. boto3)
On the second FPGA, follow the same steps.
At the top of pokemon_game.ipynb, make one FPGA have THIS_PLAYER  = 0 and the other THIS_PLAYER = 1.
*Note that dynamodb block will need to get updated for the access keys.
Run the block on both boards and the rest should be intuative.
