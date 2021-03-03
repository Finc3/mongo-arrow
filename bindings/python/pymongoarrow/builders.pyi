# Copyright 2021-present MongoDB, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


cdef class _ArrayBuilderBase:
    def append_values(self, values):
        for value in values:
            self.append(value)


cdef class Int32Builder(_ArrayBuilderBase):
    cdef:
        shared_ptr[CInt32Builder] builder

    def __cinit__(self, MemoryPool memory_pool=None):
        cdef CMemoryPool* pool = maybe_unbox_memory_pool(memory_pool)
        self.builder.reset(new CInt32Builder(pool))

    def append_null(self):
        self.builder.get().AppendNull()

    def __len__(self):
        return self.builder.get().length()

    def append(self, value):
        if value is None or value is np.nan:
            self.builder.get().AppendNull()
        elif isinstance(value, int):
            self.builder.get().Append(value)
        else:
            raise TypeError('Int32Builder only accepts integer objects')

    def finish(self):
        cdef shared_ptr[CArray] out
        with nogil:
            self.builder.get().Finish(&out)
        return pyarrow_wrap_array(out)

    cdef shared_ptr[CInt32Builder] unwrap(self):
        return self.builder


cdef class Int64Builder(_ArrayBuilderBase):
    cdef:
        shared_ptr[CInt64Builder] builder

    def __cinit__(self, MemoryPool memory_pool=None):
        cdef CMemoryPool* pool = maybe_unbox_memory_pool(memory_pool)
        self.builder.reset(new CInt64Builder(pool))

    def append_null(self):
        self.builder.get().AppendNull()

    def __len__(self):
        return self.builder.get().length()

    def append(self, value):
        if value is None or value is np.nan:
            self.builder.get().AppendNull()
        elif isinstance(value, int):
            self.builder.get().Append(value)
        else:
            raise TypeError('Int64Builder only accepts integer objects')

    def finish(self):
        cdef shared_ptr[CArray] out
        with nogil:
            self.builder.get().Finish(&out)
        return pyarrow_wrap_array(out)

    cdef shared_ptr[CInt64Builder] unwrap(self):
        return self.builder


cdef class DoubleBuilder(_ArrayBuilderBase):
    cdef:
        shared_ptr[CDoubleBuilder] builder

    def __cinit__(self, MemoryPool memory_pool=None):
        cdef CMemoryPool* pool = maybe_unbox_memory_pool(memory_pool)
        self.builder.reset(new CDoubleBuilder(pool))

    def append_null(self):
        self.builder.get().AppendNull()

    def __len__(self):
        return self.builder.get().length()

    def append(self, value):
        if value is None or value is np.nan:
            self.builder.get().AppendNull()
        elif isinstance(value, (int, float)):
            self.builder.get().Append(value)
        else:
            raise TypeError('DoubleBuilder only accepts floats and ints')

    def finish(self):
        cdef shared_ptr[CArray] out
        with nogil:
            self.builder.get().Finish(&out)
        return pyarrow_wrap_array(out)

    cdef shared_ptr[CDoubleBuilder] unwrap(self):
        return self.builder


cdef class DatetimeBuilder(_ArrayBuilderBase):
    cdef:
        shared_ptr[CTimestampBuilder] builder
        TimestampType dtype

    def __cinit__(self, TimestampType dtype=timestamp('ms'),
                  MemoryPool memory_pool=None):
        cdef CMemoryPool* pool = maybe_unbox_memory_pool(memory_pool)
        if dtype in (timestamp('us'), timestamp('ns')):
            raise ValueError("Microsecond resolution temporal type is not "
                             "suitable for use with MongoDB's UTC datetime "
                             "type which has resolution of milliseconds.")
        self.dtype = dtype
        self.builder.reset(new CTimestampBuilder(
            pyarrow_unwrap_data_type(self.dtype), pool))

    def append_null(self):
        self.builder.get().AppendNull()

    def __len__(self):
        return self.builder.get().length()

    def append(self, value):
        if value is None or value is np.nan:
            self.builder.get().AppendNull()
        elif isinstance(value, datetime.datetime):
            self.builder.get().Append(
                datetime_to_int64(value, self.dtype))
        else:
            raise TypeError('TimestampBuilder only accepts datetime objects')

    def finish(self):
        cdef shared_ptr[CArray] out
        with nogil:
            self.builder.get().Finish(&out)
        return pyarrow_wrap_array(out)

    @property
    def unit(self):
        return self.dtype

    cdef shared_ptr[CTimestampBuilder] unwrap(self):
        return self.builder
