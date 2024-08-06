# Copyright 2024 Google LLC All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import pytest

from google.protobuf import struct_pb2


def _make_stream_generator(iterable, explain_options=None):
    from google.cloud.firestore_v1.stream_generator import StreamGenerator

    def _inner_generator():
        for i in iterable:
            X = yield i
            if X:
                yield X

    return StreamGenerator(_inner_generator(), explain_options)


def test_stream_generator_constructor():
    from google.cloud.firestore_v1.query_profile import ExplainOptions
    from google.cloud.firestore_v1.stream_generator import StreamGenerator

    explain_options = ExplainOptions(analyze=True)
    inner_generator = object()
    inst = StreamGenerator(inner_generator, explain_options)

    assert inst._generator == inner_generator
    assert inst._explain_options == explain_options
    assert inst._explain_metrics is None


def test_stream_generator_iter():
    iterable = [(0, None), (1, None), (2, None)]
    expected_results = [0, 1, 2]
    inst = _make_stream_generator(iterable)
    actual_results = []
    for result in inst:
        actual_results.append(result)

    assert expected_results == actual_results


def test_stream_generator_next():
    iterable = [(0, None), (1, None)]
    expected_results = [0, 1]
    inst = _make_stream_generator(iterable)

    actual_results = []
    actual_results.append(next(inst))
    actual_results.append(next(inst))

    with pytest.raises(StopIteration):
        next(inst)

    assert expected_results == actual_results


def test_stream_generator_send():
    iterable = [(0, None), (1, None)]
    expected_results = [0, 1]
    inst = _make_stream_generator(iterable)

    actual_results = []
    actual_results.append(next(inst))
    assert inst.send(2) == 2
    actual_results.append(next(inst))

    with pytest.raises(StopIteration):
        next(inst)

    assert expected_results == actual_results


def test_stream_generator_throw():
    inst = _make_stream_generator([])
    with pytest.raises(ValueError):
        inst.throw(ValueError)


def test_stream_generator_close():
    expected_results = [0, 1]
    inst = _make_stream_generator(expected_results)

    inst.close()

    # Verifies that generator is closed.
    with pytest.raises(StopIteration):
        next(inst)


def test_stream_generator_explain_options():
    from google.cloud.firestore_v1.query_profile import ExplainOptions

    explain_options = ExplainOptions(analyze=True)
    inst = _make_stream_generator([], explain_options)
    assert inst.explain_options == explain_options


def test_stream_generator_explain_metrics_explain_options_analyze_true():
    import google.cloud.firestore_v1.query_profile as query_profile
    import google.cloud.firestore_v1.types.query_profile as query_profile_pb2

    iterator = [
        (1, None),
        (
            None,
            query_profile_pb2.ExplainMetrics(
                plan_summary=query_profile_pb2.PlanSummary()
            ),
        ),
        (2, None),
    ]

    explain_options = query_profile.ExplainOptions(analyze=True)
    inst = _make_stream_generator(iterator, explain_options)

    # Raise an exception if query isn't complete when explain_metrics is called.
    with pytest.raises(
        query_profile.QueryExplainError,
        match="explain_metrics not available until query is complete.",
    ):
        inst.explain_metrics

    list(inst)

    assert isinstance(inst.explain_metrics, query_profile.ExplainMetrics)


def test_stream_generator_explain_metrics_explain_options_analyze_false():
    import google.cloud.firestore_v1.query_profile as query_profile
    import google.cloud.firestore_v1.types.query_profile as query_profile_pb2

    plan_summary = query_profile_pb2.PlanSummary(
        indexes_used=struct_pb2.ListValue(values=[])
    )
    (
        {
            "indexes_used": {
                "query_scope": "Collection",
                "properties": "(foo ASC, **name** ASC)",
            }
        }
    )

    iterator = [
        (None, query_profile_pb2.ExplainMetrics(plan_summary=plan_summary)),
    ]

    explain_options = query_profile.ExplainOptions(analyze=False)
    inst = _make_stream_generator(iterator, explain_options)
    assert isinstance(inst.explain_metrics, query_profile.ExplainMetrics)


def test_stream_generator_explain_metrics_missing_explain_options_analyze_false():
    import google.cloud.firestore_v1.query_profile as query_profile

    explain_options = query_profile.ExplainOptions(analyze=False)
    inst = _make_stream_generator([("1", None)], explain_options)
    with pytest.raises(
        query_profile.QueryExplainError, match="Did not receive explain_metrics"
    ):
        inst.explain_metrics


def test_stream_generator_explain_metrics_no_explain_options():
    from google.cloud.firestore_v1.query_profile import QueryExplainError

    inst = _make_stream_generator([])

    with pytest.raises(
        QueryExplainError,
        match="explain_options not set on query.",
    ):
        inst.explain_metrics
