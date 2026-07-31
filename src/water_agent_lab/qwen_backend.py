from water_agent_lab.llm_backends import (
    LLMGenerationRequest,
    LLMGenerationResponse,
)


class OptionalDependencyError(ImportError):
    """
    Raised when optional local LLM dependencies are missing.
    """


class QwenLocalBackend:
    """
    Optional local Qwen backend.

    This backend is intentionally optional:
    - CI does not need transformers or torch.
    - Unit tests can validate import behavior without downloading a model.
    - Real model loading only happens when the class is instantiated.

    Example model names:
    - Qwen/Qwen2.5-1.5B-Instruct
    - Qwen/Qwen2.5-3B-Instruct
    - Qwen/Qwen2.5-7B-Instruct
    """

    def __init__(
        self,
        model_name_or_path: str,
        device_map: str = "auto",
        torch_dtype: str = "auto",
        max_new_tokens: int = 512,
    ) -> None:
        self.model_name_or_path = model_name_or_path
        self.device_map = device_map
        self.torch_dtype = torch_dtype
        self.max_new_tokens = max_new_tokens
        self.backend_name = "qwen-local"

        try:
            from transformers import AutoModelForCausalLM, AutoTokenizer
        except ImportError as error:
            raise OptionalDependencyError(
                "QwenLocalBackend requires optional dependencies. "
                "Install them with: uv add transformers torch accelerate"
            ) from error

        self.tokenizer = AutoTokenizer.from_pretrained(
            model_name_or_path,
            trust_remote_code=True,
        )

        self.model = AutoModelForCausalLM.from_pretrained(
            model_name_or_path,
            device_map=device_map,
            torch_dtype=torch_dtype,
            trust_remote_code=True,
        )

    def generate(self, request: LLMGenerationRequest) -> LLMGenerationResponse:
        """
        Generate text from a local Qwen instruction model.
        """
        messages = [
            {
                "role": "system",
                "content": request.system_prompt,
            },
            {
                "role": "user",
                "content": request.user_prompt,
            },
        ]

        prompt = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
        )

        model_inputs = self.tokenizer(
            [prompt],
            return_tensors="pt",
        ).to(self.model.device)

        generated_ids = self.model.generate(
            **model_inputs,
            max_new_tokens=min(request.max_tokens, self.max_new_tokens),
            temperature=request.temperature,
            do_sample=request.temperature > 0,
        )

        generated_ids = [
            output_ids[len(input_ids) :]
            for input_ids, output_ids in zip(
                model_inputs.input_ids,
                generated_ids,
                strict=True,
            )
        ]

        response_text = self.tokenizer.batch_decode(
            generated_ids,
            skip_special_tokens=True,
        )[0]

        return LLMGenerationResponse(
            text=response_text.strip(),
            model_name=self.model_name_or_path,
            backend_name=self.backend_name,
        )
