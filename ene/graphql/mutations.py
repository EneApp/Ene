#  ENE, Automatically track and sync anime watching progress
#  Copyright (C) 2018-2019 Peijun Ma, Justin Sedge
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

UPDATE_MEDIA_LIST_ENTRY = """\
mutation (
    $mediaId: Int,
    $status: MediaListStatus,
    $score: Float,
    $progress: Int,
    $customLists: [String],
    $private: Boolean,
    $notes: String,
    $startedAt: FuzzyDateInput,
    $completedAt: FuzzyDateInput,
    $repeat: Int
) {
    SaveMediaListEntry (
        mediaId: $mediaId,
        status: $status,
        score: $score,
        progress: $progress,
        customLists: $customLists,
        private: $private,
        notes: $notes,
        startedAt: $startedAt,
        completedAt: $completedAt,
        repeat: $repeat
    ) {
            id
            mediaId
            status
            score
            progress
            repeat
            private
            notes
            customLists
            startedAt {
                year
                month
                day
            }
            completedAt {
                year
                month
                day
            }
    }
}"""
