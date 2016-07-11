#!/usr/bin/env python
#
# Copyright (C) 2016 GNS3 Technologies Inc.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from unittest.mock import MagicMock
import pytest
import uuid

from tests.utils import AsyncioMagicMock


from gns3server.controller.drawing import Drawing
from gns3server.controller.project import Project


@pytest.fixture
def project(controller, async_run):
    return async_run(controller.add_project(name="Test"))


@pytest.fixture
def drawing(project):
    return Drawing(project, None, svg="<svg></svg>")


def test_init_without_uuid(project):
    drawing = Drawing(project, None, svg="<svg></svg>")
    assert drawing.id is not None


def test_init_with_uuid(project):
    id = str(uuid.uuid4())
    drawing = Drawing(project, id, svg="<svg></svg>")
    assert drawing.id == id


def test_json(project):
    i = Drawing(project, None, svg="<svg></svg>")
    assert i.__json__() == {
        "drawing_id": i.id,
        "project_id": project.id,
        "x": i.x,
        "y": i.y,
        "z": i.z,
        "svg": i.svg,
        "rotation": i.rotation
    }
    assert i.__json__(topology_dump=True) == {
        "drawing_id": i.id,
        "x": i.x,
        "y": i.y,
        "z": i.z,
        "rotation": i.rotation,
        "svg": i.svg
    }


def test_update(drawing, project, async_run, controller):
    controller._notification = AsyncioMagicMock()
    project.dump = MagicMock()

    async_run(drawing.update(x=42, svg="<svg><rect></rect></svg>"))
    assert drawing.x == 42
    args, kwargs = controller._notification.emit.call_args
    assert args[0] == "drawing.updated"
    # JSON
    assert args[1]["x"] == 42
    assert args[1]["svg"] == "<svg><rect></rect></svg>"

    async_run(drawing.update(x=12, svg="<svg><rect></rect></svg>"))
    assert drawing.x == 12
    args, kwargs = controller._notification.emit.call_args
    assert args[0] == "drawing.updated"
    # JSON
    assert args[1]["x"] == 12
    # To avoid spamming client with large data we don't send the svg if the SVG didn't change
    assert "svg" not in args[1]

    assert project.dump.called