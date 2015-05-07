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

import React, {PropTypes} from "react";
import {Grid, Row, Col, ModalTrigger, ButtonGroup, Button} from "react-bootstrap";
import ListenerMixin from "alt/mixins/ListenerMixin";
import values from "lodash/object/values";
import classNames from "classnames";

import PageActions from "actions/PageActions.js";
import workflowStore from "stores/WorkflowStore.js";
import pageStore from "stores/PageStore.js";
import {getImageUrl} from "utils/WebAPIUtils";
import Pagination from "components/utility/Pagination";
import PagePreview from "components/utility/PagePreview";
import Metadata from "components/utility/Metadata";
import Icon from "components/utility/Icon";
import LightboxModal from "components/modals/LightboxModal";

const PageContainer = React.createClass({
  displayName: "PageContainer",
  propTypes: {
    page: PropTypes.object.isRequired,
    onSelected: PropTypes.func.isRequired,
    onClick: PropTypes.func.isRequired
  },

  render() {
    return (
      <div className="page-container">
        <PagePreview page={this.props.page} thumbnail={true}
                     onClick={this.props.onClick} />
      </div>
    );
  }
});

export default React.createClass({
  displayName: "WorkflowDetails",
  mixins: [ListenerMixin],
  propTypes: {
    params: PropTypes.object,
    query: PropTypes.object
  },

  componentDidMount() {
    this.listenTo(workflowStore, this.handleWorkflowChange);
    this.listenTo(pageStore, this.handlePageChange);
  },

  getInitialState() {
    return {
      workflow: workflowStore.getState().workflows[this.props.params.id],
      pages: pageStore.getState().pages[this.props.params.id],
      perPage: 24,
      pageOffset: 0,
      showInLightbox: undefined
    };
  },

  handleWorkflowChange() {
    this.setState({
      workflow: workflowStore.getState().workflows[this.props.params.id]
    });
  },

  handlePageChange() {
    this.setState({
      pages: pageStore.getState().pages[this.props.params.id]
    });
  },

  handleGridBrowse(selected) {
    this.setState({
      pageOffset: Math.floor((selected - 1) * this.state.perPage)
    });
  },

  handlePageCropped(cropParams) {
    PageActions.updateOne({
      "workflow_id": this.state.showInLightbox.workflow_id,
      "capture_num": this.state.showInLightbox.capture_num,
      "processing_params": {crop: cropParams}
    });
    this.setState({
      showInLightbox: null
    });
  },

  getPageNum() {
    return Math.floor(this.state.pageOffset / this.state.perPage) + 1;
  },

  render() {
    const {pages, pageOffset, perPage} = this.state;
    const totalPages = Math.ceil(Object.keys(pages).length / perPage);
    return (
      <div>
        <h3>Metadata</h3>
        <Metadata metadata={this.state.workflow.metadata} />

        <h3>Pages</h3>
        <Grid>
          <Row>
            {values(pages).slice(pageOffset, pageOffset + perPage)
              .map((page) => {
                return (
                  <Col xs={6} md={3} lg={2} key={page.capture_num}>
                    <PageContainer
                      page={page}
                      onClick={() => this.setState({showInLightbox: page})} />
                  </Col>
                );
              })}
          </Row>
        </Grid>
        <Pagination pageNum={this.getPageNum()} totalPages={totalPages}
                    onPageChange={this.handleGridBrowse} rangeDisplay={3}
                    marginDisplay={1} />
        {this.state.showInLightbox &&
          <LightboxModal pages={values(this.state.pages)}
                         startPage={this.state.showInLightbox}
                         enableCrop={true} onCropped={this.handlePageCropped}
                         onRequestHide={() => this.setState({showInLightbox: undefined})}/>}
      </div>
    );
  }
})