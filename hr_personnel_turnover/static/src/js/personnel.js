
odoo.define('hr_personnel_turnover.personnelBasicModel', function (require) {
    "use strict";


    var BasicModel = require('web.BasicModel');

    BasicModel.include({
        _generateChanges: function (record, options) {
            let changes = this._super(record, options);
            
            let moveModels = ["hr.contract", "hr.employee"];
            if(moveModels.indexOf(record.model) !== -1 && !isNaN(record.res_id)){

                // this is a list of fields that have to be registerd
                let moveFields = [
                    "department_id",
                    "resource_calendar_id",
                    "wage",
                    "parent_id",
                    "coach_custom_id",
                    "job_id"
                ]
                let moveChanges = {};
                let fieldName;
                let deleteFields = false;
                
                for(fieldName in changes){
                    if (moveFields.indexOf(fieldName) !== -1){
                        moveChanges[fieldName] = changes[fieldName];
                        deleteFields = true;
                    }
                }
                
                if(deleteFields){
                    for (var key in changes) {
                        if (changes.hasOwnProperty(key)) {
                            delete changes[key];
                        }
                    }

                    this.do_action({
                        type: 'ir.actions.act_window',
                        name: 'Registrar movimiento',
                        res_model: 'wizard.personnel.turnover',
                        views: [[false, 'form']],
                        view_type: 'form', 
                        view_mode: 'form', 
                        target: 'new',
                        context: {
                            model: record.model,
                            value: record.res_id,
                            changes: moveChanges,
                        },
                    });
                }
            }

            return changes;
        }
    });

});
