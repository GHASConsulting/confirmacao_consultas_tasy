"""
Utilitários para normalização e formatação de telefone.

Padrão usado para envio (Botconversa/N8N): apenas dígitos, com DDI no início.
Ex.: 5531999999999 (Brasil 55 + DDD 31 + número).
"""

from typing import Optional


def normalizar_telefone(telefone: Optional[str]) -> str:
    """
    Retorna apenas os dígitos do telefone (para comparação e armazenamento).

    Ex.: "(31) 99999-9999" -> "31999999999"
         "+55 31 99999-9999" -> "5531999999999"
    """
    if not telefone:
        return ""
    return "".join(c for c in str(telefone).strip() if c.isdigit())


def telefone_para_envio(
    nr_telefone: Optional[str],
    nr_ddi: Optional[str] = None,
    ddi_padrao: str = "55",
) -> str:
    """
    Formata telefone no padrão para envio (Botconversa/WhatsApp): só dígitos, DDI + número.

    - Remove espaços, traços, parênteses.
    - Se nr_ddi for informado e o número ainda não começar com ele, coloca na frente.
    - Se nr_ddi for vazio e o número tiver 10 ou 11 dígitos (BR), usa ddi_padrao (55).

    Returns:
        String só com dígitos, ex.: 5531999999999
    """
    tel = normalizar_telefone(nr_telefone)
    if not tel:
        return ""

    ddi = (nr_ddi or "").strip() or ddi_padrao
    ddi_digitos = "".join(c for c in ddi if c.isdigit()) or ddi_padrao

    # Já tem DDI no início (ex.: 5531999999999)
    if ddi_digitos and tel.startswith(ddi_digitos):
        return tel
    if ddi_digitos:
        return f"{ddi_digitos}{tel}"
    return tel
