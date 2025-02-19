import pytest

import json

import great_expectations as ge
import great_expectations.render as render
from great_expectations.render.renderer import (
    DescriptivePageRenderer,
    DescriptiveColumnSectionRenderer,
    PrescriptiveColumnSectionRenderer,
    PrescriptivePageRenderer,
)
from great_expectations.render.view import DefaultJinjaPageView


def test_render_template():
    assert render.view.view.render_string_template({
        "template": "It was the $first_adj of times; it was the $second_adj of times.",
        "params": {
            "first_adj": "best",
            "second_adj": "worst",
        }
    }) == "It was the best of times; it was the worst of times."

    assert render.view.view.render_string_template({
        "template": "It was the $first_adj of times; it was the $second_adj of times.",
        "params": {
            "first_adj": "best",
            "second_adj": "worst",
        },
        "styling": {
            "default": {
                "classes": ["badge", "badge-warning"],
            }
        }
    }) == 'It was the <span class="badge badge-warning" >best</span> of times; it was the <span class="badge badge-warning" >worst</span> of times.'

    assert render.view.view.render_string_template({
        "template": "It was the $first_adj of times; it was the $second_adj of times.",
        "params": {
            "first_adj": "best",
            "second_adj": "worst",
        },
        "styling": {
            "default": {
                "classes": ["badge", "badge-warning"],
            },
            "params": {
                "first_adj": {
                    "classes": ["badge-error"],
                }
            }
        }
    }) == 'It was the <span class="badge-error" >best</span> of times; it was the <span class="badge badge-warning" >worst</span> of times.'

    assert render.view.view.render_string_template({
        "template": "It was the $first_adj of times; it was the $second_adj of times.",
        "params": {
            "first_adj": "best",
            "second_adj": "worst",
        },
        "styling": {
            "params": {
                "first_adj": {
                    "classes": ["badge", "badge-warning"],
                }
            }
        }
    }) == 'It was the <span class="badge badge-warning" >best</span> of times; it was the worst of times.'

    assert render.view.view.render_string_template({
        "template": "It was the $first_adj of times; it was the $second_adj of times.",
        "params": {
            "first_adj": "best",
            "second_adj": "worst",
        },
        "styling": {
            "params": {
                "first_adj": {
                    "classes": ["badge", "badge-warning"],
                    "attributes": {
                        "role": "alert"
                    },
                    "styles": {
                        "padding": "5px"
                    }
                }
            }
        }
    }) == 'It was the <span class="badge badge-warning" role="alert" style="padding:5px;" >best</span> of times; it was the worst of times.'
