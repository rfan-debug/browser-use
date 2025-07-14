import asyncio

from bubus import BaseEvent, EventBus


class SomeOtherEvent(BaseEvent):
	pass


class MainEvent(BaseEvent):
	pass


class ProcessTaskEvent(BaseEvent):
	task_id: int


class StopBusEvent(BaseEvent):
	pass


bus = EventBus()


async def child_handler(event: SomeOtherEvent):
	await asyncio.sleep(0.1)
	return 'xzy123'


async def main_handler(event: MainEvent):
	# enqueue event for processing after main_handler exits
	child_event = bus.dispatch(SomeOtherEvent())

	# can also await child events to process immediately instead of adding to FIFO queue
	completed_child_event = await child_event
	final_res = await completed_child_event.event_result()
	return f'result from awaiting child event: {final_res}'  # 'xyz123'


async def async_main():
	bus.on(SomeOtherEvent, child_handler)
	bus.on(MainEvent, main_handler)
	mm = await bus.dispatch(MainEvent()).event_result()
	print(mm)
	await bus.wait_until_idle()
	# result from awaiting child event: xyz123


def process_task_handler(event: ProcessTaskEvent):
	print(event.task_id)


async def stop_bus_handler(event: StopBusEvent):
	print('Shutting down the bus')
	await bus.stop(clear=True, timeout=3)


async def async_main2():
	# Events are processed in the order they were dispatched
	for i in range(10):
		bus.dispatch(ProcessTaskEvent(task_id=i))

	# The last event is to stop the bus/
	bus.dispatch(StopBusEvent())

	bus.on(ProcessTaskEvent, process_task_handler)
	bus.on(StopBusEvent, stop_bus_handler)
	# Even with async handlers, order is preserved
	print('awaiting?')
	await bus.wait_until_idle()


if __name__ == '__main__':
	res = asyncio.run(async_main())
	print(res)
