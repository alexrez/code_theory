usage: linearcode_n_errors.py mode param

Linear error-correcting code.

optional arguments: -h, --help show this help message and exit

mode: valid modes

{gencode,coder,decoder}

gencode             generating linear code and decode vector

    usage: linearcode_n_errors.py gencode [-h] [--out-file OUT] r n t

    positional arguments:
      r               number of check bits
      n               length of a code word
      t               number of error to correct

    optional arguments:
      -h, --help      show this help message and exit
      --out-file OUT  file to write information for coder/decpder (default:
                      code_information.pickle)


coder               code message by spliting in blocks with length k and
                    adding error vector

    usage: linearcode_n_errors.py coder [-h] [-e E] inputfile m

    positional arguments:
      inputfile   file whith information for coder in pickle format
      m           message

    optional arguments:
      -h, --help  show this help message and exit
      -e E        error


decoder             decode message by spliting in blocks with length n and
                    subtracting error vector

    usage: linearcode_n_errors.py decoder [-h] inputfile y

    positional arguments:
      inputfile   file whith information for decoder in pickle format
      y           message with error

    optional arguments:
      -h, --help  show this help message and exit
