CREATE TABLE datagen (
    id INT
) WITH (
      'connector' = 'datagen',
      'number-of-rows' = '{number_of_rows}'
      );

select * from datagen WHERE remote_trace(true, 'TRACE_ME', id);