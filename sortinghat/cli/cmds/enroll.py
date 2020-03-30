# -*- coding: utf-8 -*-
#
# Copyright (C) 2014-2020 Bitergia
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
# Authors:
#     Santiago Dueñas <sduenas@bitergia.com>
#

import click

from sgqlc.operation import Operation

from grimoirelab_toolkit.datetime import (str_to_datetime,
                                          InvalidDateError)

from ..client import SortingHatSchema
from ..utils import (connect,
                     sh_client_cmd_options,
                     sh_client)


@click.command()
@sh_client_cmd_options
@click.argument('uuid')
@click.argument('organization')
@click.option('--from-date',
              help="Date when the enrollment starts")
@click.option('--to-date',
              help="Date when the enrollment ends")
@sh_client
def enroll(ctx, uuid, organization, from_date, to_date, **extra):
    """Enroll a unique identity in an organization.

    This command enrolls the unique identity <uuid> in the
    given <organization>. Both identity and organization must
    exist before adding the new enrollment to the registry.

    The period of the enrollment can be given with the options
    <from_date> and <to_date>, where 'from_date <= to_date'.
    Valid dates should follow ISO 8601 standard (e.g
    'YYYY-MM-DD' for dates; 'YYYY-MM-DD hh:mm:ss±hhmm' for
    timestamps). The default values for these dates are
    '1900-01-01' and '2100-01-01' in UTC.

    Existing enrollments for the same unique identity and
    organization which overlap with the new period will be
    automatically merged into a single enrollment.

    If the given period for that enrollment is enclosed by
    one already stored, the command will return an error.

    UUID: unique identity to enroll

    ORGANIZATION: name of organization
    """
    with connect(ctx.obj) as conn:
        try:
            if from_date:
                from_date = str_to_datetime(from_date)
            if to_date:
                to_date = str_to_datetime(to_date)
        except InvalidDateError as exc:
            raise click.ClickException(str(exc))

        _enroll_identity(conn, uuid=uuid,
                         organization=organization,
                         from_date=from_date,
                         to_date=to_date)


def _enroll_identity(conn, **kwargs):
    """Run a server operation to enroll an identity."""

    args = {k: v for k, v in kwargs.items() if v is not None}

    op = Operation(SortingHatSchema.SortingHatMutation)
    op.enroll(**args)
    op.enroll.uuid()

    result = conn.execute(op)

    return result['data']['enroll']['uuid']
