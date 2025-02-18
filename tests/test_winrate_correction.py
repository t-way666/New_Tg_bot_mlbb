import unittest
from unittest.mock import MagicMock, patch
from handlers.winrate_correction import send_winrate_correction, calculate_additional_matches

class TestWinrateCorrection(unittest.TestCase):
    def setUp(self):
        self.bot = MagicMock()
        send_winrate_correction(self.bot)

    def test_calculate_additional_matches(self):
        self.assertEqual(calculate_additional_matches(55, 70, 60, 70), 18)

    @patch('handlers.winrate_correction.bot.reply_to')
    @patch('handlers.winrate_correction.bot.register_next_step_handler')
    def test_send_winrate_correction(self, mock_register_next_step_handler, mock_reply_to):
        message = MagicMock()
        message.text = "55"
        message.from_user.first_name = "TestUser"
        
        # Simulate /winrate_correction command
        handler = self.bot.message_handler.call_args[0][1]
        handler(message)
        mock_reply_to.assert_called_with(message, "Введите ваш текущий винрейт (в процентах):")

        # Simulate entering current winrate
        message.text = "55"
        handler = mock_register_next_step_handler.call_args[0][1]
        handler(message, self.bot)
        mock_reply_to.assert_called_with(message, "Введите количество уже сыгранных матчей:")

        # Simulate entering played matches
        message.text = "70"
        handler = mock_register_next_step_handler.call_args[0][1]
        handler(message, self.bot, 55.0)
        mock_reply_to.assert_called_with(message, "Введите ожидаемый винрейт в будущих играх (в процентах):")

        # Simulate entering expected winrate
        message.text = "60"
        handler = mock_register_next_step_handler.call_args[0][1]
        handler(message, self.bot, 55.0, 70)
        mock_reply_to.assert_called_with(message, "Введите желаемый общий винрейт (в процентах):")

        # Simulate entering desired winrate
        message.text = "70"
        handler = mock_register_next_step_handler.call_args[0][1]
        handler(message, self.bot, 55.0, 70, 60.0)
        mock_reply_to.assert_called_with(message, "Вам нужно сыграть примерно 18 дополнительных матчей, чтобы достичь желаемого винрейта.")

if __name__ == '__main__':
    unittest.main()