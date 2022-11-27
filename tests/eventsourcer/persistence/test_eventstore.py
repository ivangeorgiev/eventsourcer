from unittest.mock import Mock, call
import pytest
from eventsourcer.persistence.eventstore import NoneDecoder, NoneEncoder, EventStore


@pytest.mark.unit
class TestEventStoreClass:
    @pytest.fixture(name="mock_encoder")
    def given_mock_encoder(self):
        encoder = Mock()
        return encoder

    @pytest.fixture(name="mock_decoder")
    def given_mock_decoder(self):
        return Mock()

    @pytest.fixture(name="mock_query")
    def given_mock_query(self):
        return Mock()

    @pytest.fixture(name="mock_writer")
    def given_mock_writer(self):
        return Mock()

    def test_get_should_return_list_of_decoded_events(self, mock_decoder, mock_query):
        mock_decoder.decode.side_effect = [1, 2]
        stored_events = ["a", "b"]
        originator_id = "abcd"
        mock_query.execute.return_value = stored_events

        store = EventStore()
        store.decoder = mock_decoder
        store.query = mock_query

        retrieved_events = store.get(originator_id)

        assert list(retrieved_events) == [1, 2]
        mock_query.execute.assert_called_once_with(originator_id)

    def test_put_should_insert_encoded_events(self, mock_encoder, mock_writer):
        stored_events = ["a", "b"]
        events = [1, 2]
        mock_encoder.encode.side_effect = stored_events

        store = EventStore()
        store.encoder = mock_encoder
        store.writer = mock_writer

        store.put(events)

        mock_writer.append_all.assert_called_once()
        writer_called_with_events = list(mock_writer.append_all.call_args[0][0])
        assert writer_called_with_events == stored_events

        expected_encoder_calls = [call(e) for e in events]
        mock_encoder.encode.assert_has_calls(expected_encoder_calls, any_order=True)


@pytest.mark.unit
class TestNoneEncoderClass:
    def test_encode_should_return_input_unchanged(self):
        encoder = NoneEncoder()
        event = Mock()
        assert encoder.encode(event) is event


@pytest.mark.unit
class TestNoneDecoderClass:
    def test_decode_should_return_input_unchanged(self):
        decoder = NoneDecoder()
        event = Mock()
        assert decoder.decode(event) is event