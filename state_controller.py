# state_controller.py


class StateControllerMixin:
    def set_mode(self, mode, index=None):
        self.mode = mode
        self.selected_index = index
        if mode == "create":
            self.editor_title.config(text="NOUVELLE CARTE", fg="#FFFFFF")
            self.editor_subtitle.config(text="Configurez un nouveau sticker")
            self.btn_add_update.config(text="+  AJOUTER AU LOT", bg="#2ECC71",
                                        activebackground="#27AE60")
            self.btn_new_card.config(state="disabled", bg="#1A3A25")
        else:
            card = self.lot[index]
            self.editor_title.config(text="ÉDITER : " + card["parfum"].upper(), fg="#FFD700")
            self.editor_subtitle.config(text="Modifiez les paramètres de cette carte")
            self.btn_add_update.config(text="◈  METTRE À JOUR", bg="#1F5EFF",
                                        activebackground="#1447CC")
            self.btn_new_card.config(state="normal", bg="#2ECC71")
        self.update_gallery_selection()

    def set_gender(self, gender):
        self.gender_var.set(gender)
        self.update_gender_buttons()
        self.update_preview()

    def set_pattern(self, pattern):
        self.pattern_var.set(pattern)
        self.update_pattern_buttons()
        self.update_preview()

    def set_phone_color(self, color):
        self.phone_color_var.set(color)
        self.update_phone_color_buttons()
        self.update_preview()

    def set_phone_bg(self, bg_type):
        self.phone_bg_var.set(bg_type)
        self.update_phone_bg_buttons()
        self.update_preview()

    def update_gender_buttons(self):
        is_male = self.gender_var.get() == "male"
        self.btn_male.config(bg="#1F5EFF" if is_male else "#1E1E32",
                             fg="white" if is_male else "#555")
        self.btn_female.config(bg="#FF5FA2" if not is_male else "#1E1E32",
                               fg="white" if not is_male else "#555")

    def update_pattern_buttons(self):
        active = self.pattern_var.get()
        for key, (btn, lbl) in self._pattern_btns.items():
            cell = self._pattern_cells[key]
            if key == active:
                btn.config(bg="#2A2A45", fg="white")
                lbl.config(fg="white")
                cell.config(highlightbackground="#1F5EFF", highlightthickness=1)
            else:
                btn.config(bg="#1E1E32", fg="#555")
                lbl.config(fg="#555")
                cell.config(highlightbackground="#12121F", highlightthickness=0)

    def update_phone_color_buttons(self):
        active = self.phone_color_var.get()
        self.btn_pc_white.config(bg="#333" if active == "white" else "#1E1E32",
                                 fg="white" if active == "white" else "#555")
        self.btn_pc_black.config(bg="#333" if active == "black" else "#1E1E32",
                                 fg="white" if active == "black" else "#555")

    def update_phone_bg_buttons(self):
        active = self.phone_bg_var.get()
        mapping = {"none": self.btn_pb_none, "line_outer": self.btn_pb_line, "bg_outer": self.btn_pb_fill}
        for key, btn in mapping.items():
            btn.config(bg="#333" if active == key else "#1E1E32",
                       fg="white" if active == key else "#555")