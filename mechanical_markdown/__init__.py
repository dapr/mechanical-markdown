"""
Copyright (c) Microsoft Corporation.
Licensed under the MIT License.
"""

__version__ = '0.1.7'

from mechanical_markdown.recipe import Recipe as MechanicalMarkdown
from mechanical_markdown.parsers import MarkdownAnnotationError

__all__ = [MechanicalMarkdown, MarkdownAnnotationError]
