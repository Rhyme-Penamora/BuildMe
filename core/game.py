REPLACE_LINES:255-263
            # FIX: handle expansion popup before anything else
            if self._expansion_popup is not None:
                popup = self._expansion_popup

                if popup.handle_event(event):
                    if self._expansion_popup is not None and not popup.active:
                        self._expansion_popup = None
                    continue