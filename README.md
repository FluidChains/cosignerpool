# Cosigner Pool for electrum bitcoin wallet

[![Build Status](https://travis-ci.com/bchr73/cosignerpool.svg?token=QWJNTJDWRxkuUHPftfyv&branch=master)](https://travis-ci.org/bchr73/cosignerpool)

Cosigner Pool is a multi-threaded, XMLRPC wrapper for LevelDB in memory, storage, and retrieval. It is designed to be used with the electrum bitcoin wallet cosigner pool plugin. 

Some features implemented in this version include:
  - Support for threads
  - Better logging (w. Python logging)
  - Atomic reads and writes

A brief summary of the implementation follows:

> The locking structure for the cosigner pool is based on the [2nd] [readers-writers problem](https://en.wikipedia.org/wiki/Readers%E2%80%93writers_problem#Second_readers-writers_problem), in which preference is granted to the writers.

Methods include:
```py
def get(key):
    # atomic read from db
    
def put(key, value):
    # atomic write to db
    
def delete(key):
    # atomic delete from db
```

Some additonal methods are included for testing server is alive, and for debugging purposes:
```py
def announce(idx):
    # log announce wallet id when connected
    
def message(idx, message):
    # log info for when debugging multiple wallets

def ping():
    # server 'is-alive'
```

### Installation

Cosigner Pool requires [python3](https://docs.python.org/3/), [pip3](https://pip.pypa.io/en/stable/), and [plyvel](https://pypi.org/project/plyvel/) to run.

Install the dependencies and start the server.

```sh
$ cd cosignerpool
$ pip install -r requirements.txt
$ ./src/start
```

By default, cosignerpool will run on localhost:8080. To run on a different port:

```sh
$ cd src
$ python3 cosignerpool <HOST> <PORT>
```

### Logging

All logging information is directed to:
```sh
$ ../cosignerpool/src/log/server.log
...
[1972-03-09 20:08:27,946] INFO: PUT :: c31e254923f8ec9918f4851131168f43fe3b18a004a00cd3cf06a833, 708
[1972-03-09 20:08:28,589] INFO: PUT :: 1ffee194c949b1ebd99959bf9b27874bb5fcf2f49edd7a489e526457, 708
[1972-03-09 20:08:29,232] INFO: PUT :: 2661972c2753e70d21db6f25f3c0302ece0bfa9c8acf379af1bf5023, 708
[1972-03-09 20:08:29,880] INFO: PUT :: f94ff47403cb12e0adbd22b512c3b9c5f236598dae5cd7b78ef06abd, 708
[1972-03-09 20:08:51,826] INFO: GET :: a6eabc4050fe068d3be1d5bd4f5107b0a4a2188d4586f73a533d1e20, 708
[1972-03-09 20:08:55,289] INFO: DEL :: 944f6567379169c87531b3bf0a0b9a116ed3c59ded4fe88a4ea263d4
[1972-03-09 20:09:59,846] INFO: GET :: 6f77caca57e92a7383240cd6e9d9646156ac747016a58f0cd45b6152, 708
[1972-03-09 20:10:02,426] INFO: ANN :: 5349ebe0be274b8abb5a172d96d15a66
[1972-03-09 20:10:32,958] INFO: MSG :: 5349ebe0be274b8abb5a172d96d15a66, 'message from wallet'
...
```

