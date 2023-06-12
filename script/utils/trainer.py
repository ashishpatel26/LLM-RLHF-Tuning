import os,sys,logging
import torch
from transformers import Trainer,PreTrainedModel
from transformers.modeling_utils import unwrap_model
from typing import Optional, Tuple
from peft import get_peft_model,get_peft_model_state_dict

logger = logging.getLogger(__name__)


# WEIGHTS_NAME = "pytorch_model.bin"
WEIGHTS_NAME = "adapter_model.bin"
TRAINING_ARGS_NAME = "training_args.bin"


class PeftTrainer(Trainer):
    def __init__(self, args, **kwargs):
        super().__init__(**kwargs)
        self.args = args 

    def _save(self, output_dir: Optional[str] = None, state_dict=None):
        # If we are executing this function, we are the process zero, so we don't check for that.
        output_dir = output_dir if output_dir is not None else self.args.output_dir
        os.makedirs(output_dir, exist_ok=True)
        logger.info(f"Saving model checkpoint to {output_dir}")

        if not isinstance(self.model, PreTrainedModel):
            if state_dict is None:
                state_dict = self.model.state_dict()
            
            if isinstance(unwrap_model(self.model), PreTrainedModel):       ######### 
                unwrap_model(self.model).save_pretrained(output_dir, state_dict=state_dict)
            else:
                logger.info("Trainer.model is not a `PreTrainedModel`, only saving its state dict.")
                # torch.save(state_dict, os.path.join(output_dir, WEIGHTS_NAME))
                torch.save(get_peft_model_state_dict(self.model, state_dict), os.path.join(output_dir, WEIGHTS_NAME))
            ##### add code 
            try:
                unwrap_model(self.model).peft_config.save_pretrained(output_dir)
            except AttributeError:
                unwrap_model(self.model).peft_config['default'].save_pretrained(output_dir)
        else:
            self.model.save_pretrained(output_dir, state_dict=state_dict)

        if self.tokenizer is not None:
            self.tokenizer.save_pretrained(output_dir)

        # Good practice: save your training arguments together with the trained model
        torch.save(self.args, os.path.join(output_dir, TRAINING_ARGS_NAME))


















