## Collection of defines to be sued
from enum import Enum
from tabnanny import check
import vsc
import copy

## Used to error out
def error_out(header,message):
    assert(0,header+message)

## Access TYPE
class path_t(Enum):
    FRONTDOOR       = 1
    BACKDOOR        = 2
    USER_FRONTDOOR  = 3
    
## Check TYPE
class check_t(Enum):
    CHECK       = 1
    NO_CHECK    = 2

## Status TYPE
class elem_kind(Enum):
    IS_OK       = 1
    IS_NOT_OK   = 2

## Predict Type
class predict_t(Enum):
    PREDICT_WRITE   = 1
    PREDICT_READ    = 2
    PREDICT_DIRECT  = 3

##
class elem_kind_e(Enum):
    pass

##
class access_e(Enum):
    PYUVM_READ  = 0
    PYUVM_WRITE = 1

##
class pyuvm_resp_t(Enum):
    PASS_RESP  = 0
    ERROR_RESP = 1

## New Decorator class with randomization option
## If the randomization is switched off then the decorator will no more use
## py_vsc but it just disables it allowing user to use local methods if needed
def rand_enable(use_pyvsc: bool):
    class enable_rand:
        ## Accept class as argument
        def __init__(self, cls) -> None:
            self.cls = cls

        ## operate on CLS init inupt argument    
        def __call__(self):
            if(use_pyvsc == True):
                return vsc.randobj
            else: 
                # Return the function unchanged, not decorated. if use_pyvsc is not enabled
                return self.cls
    return enable_rand

## Global to be set in case we wanna use the VSC package
enable_pyvsc = False

## Global to be set in case we wanna use the auto prediction
enable_auto_predict = True

## Global enable bit for error response in case of NO-EFFECT action based on the access type
enable_throw_error_response_on_read = False
enable_throw_error_response_on_write = False

##
class uvm_reg_bus_op:
    kind:       access_e
    addr:       int 
    data:       int
    n_bits:     int
    byte_en:    bool
    status:     pyuvm_resp_t

## List of uvm_reg errors to be collected
class uvm_reg_error_decoder(Enum):
    FIELD_CANNOT_BE_NONE = 0
    FIELD_ALREADY_ADDED = 1
    FIELD_DOESNT_FIT_INTO_REG = 2
    FIELD_OVERLAPPING_ERROR = 3
    