"""Shared enums for business constrained fields."""
from enum import Enum


class StageEnum(str, Enum):
    刚结课 = "刚结课"
    已激活 = "已激活"
    已联系 = "已联系"
    有兴趣 = "有兴趣"
    明确需求 = "明确需求"
    高意向 = "高意向"
    已成交 = "已成交"
    沉默 = "沉默"
    流失 = "流失"
