/** @odoo-module **/
import { Dialog } from "@web/core/dialog/dialog";
import { patch } from "@web/core/utils/patch";

patch(Dialog.prototype, "Personnel Dialog", {
    close() {
        this._super();

        try {
            let model = this.props.actionProps.resModel
            if (model === "wizard.personnel.turnover"){
                location.reload(true);
            }
        } catch (error) { null; }
    },
});

