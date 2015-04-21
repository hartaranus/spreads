/*
 * Spreads - Modular workflow assistant for book digitization
 * Copyright (C) 2013-2015 Johannes Baiter <johannes.baiter@gmail.com>
 *
 * This file is part of Spreads.
 *
 * Spreads is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as
 * published by the Free Software Foundation, either version 3 of the
 * License, or (at your option) any later version.
 *
 * Spreads is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Affero General Public License for more details.
 *
 * You should have received a copy of the GNU Affero General Public License
 * along with Spreads.  If not, see <http://www.gnu.org/licenses/>.
 */

import alt from "alt";
import WorkflowActions from "actions/WorkflowActions";
import PageActions from "actions/PageActions";

class PageStore {
  constructor() {
    this.pages = {};

    this.bindListeners({
      handleWorkflowCreated: WorkflowActions.REMOTELY_CREATED,
      handleWorkflowDeleted: WorkflowActions.REMOTELY_DELETED,
      handleDeleted: PageActions.REMOTELY_DELETED,
      handleUpdated: PageActions.REMOTELY_UPDATED
    });
  }

  handleDeleted(page) {
    delete this.pages[page.workflow_id][page.capture_num];
  }

  handleUpdated(page) {
    this.pages[page.workflow_id][page.capture_num] = page;
  }

  handleWorkflowCreated(workflow) {
    this.pages[workflow.id] = {};
  }

  handleWorkflowDeleted(workflow) {
    delete this.pages[workflow.id];
  }
}

export default alt.createStore(PageStore, "PageStore");
