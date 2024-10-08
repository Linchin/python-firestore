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

"""Classes for iterating over stream results async for the Google Cloud
Firestore API.
"""

from typing import Any, AsyncGenerator, Awaitable, TypeVar


T = TypeVar("T")


class AsyncStreamGenerator(AsyncGenerator[T, Any]):
    """Asynchronous generator for the streamed results."""

    def __init__(self, response_generator: AsyncGenerator[T, Any]):
        self._generator = response_generator

    def __aiter__(self) -> AsyncGenerator[T, Any]:
        return self

    def __anext__(self) -> Awaitable[T]:
        return self._generator.__anext__()

    def asend(self, value=None) -> Awaitable[Any]:
        return self._generator.asend(value)

    def athrow(self, exp=None) -> Awaitable[Any]:
        return self._generator.athrow(exp)

    def aclose(self):
        return self._generator.aclose()
