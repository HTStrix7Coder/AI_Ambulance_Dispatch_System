import React, { useState } from "react";
import { Col, Container, Row } from "reactstrap";
import MedicalWidgets from "./MedicalWidgets";
import MedicalSection from "./MedicalSection";

const DashboardEcommerce = () => {
  document.title = "Dashboard | AI Medical System";

  const [rightColumn, setRightColumn] = useState(false);
  const toggleRightColumn = () => {
    setRightColumn(!rightColumn);
  };

  return (
    <React.Fragment>
      <div className="page-content">
        <Container fluid>
          <Row>
            <Col>
              <div className="h-100">
                <MedicalSection rightClickBtn={toggleRightColumn} />
                <Row>
                  <MedicalWidgets />
                </Row>
                {/* Recent Cases removed as requested */}
              </div>
            </Col>
          </Row>
        </Container>
      </div>
    </React.Fragment>
  );
};

export default DashboardEcommerce;
