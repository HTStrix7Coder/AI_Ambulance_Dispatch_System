import React from 'react';
import { Link } from 'react-router-dom';
import { Card, CardBody, CardHeader, Col } from 'reactstrap';
import { recentCases } from '../../common/data/dashboardMedical';

const RecentCases = () => {
    return (
        <React.Fragment>
            <Col xl={12}>
                <Card>
                    <CardHeader className="align-items-center d-flex">
                        <h4 className="card-title mb-0 flex-grow-1">Recent Cases</h4>
                        <div className="flex-shrink-0">
                            <Link to="/cases" className="btn btn-soft-info btn-sm">View All Cases</Link>
                        </div>
                    </CardHeader>

                    <CardBody>
                        <div className="table-responsive table-card">
                            <table className="table table-borderless table-centered align-middle table-nowrap mb-0">
                                <thead className="text-muted table-light">
                                    <tr>
                                        <th scope="col">Case ID</th>
                                        <th scope="col">Patient</th>
                                        <th scope="col">Assigned Doctor</th>
                                        <th scope="col">Date</th>
                                        <th scope="col">Priority</th>
                                        <th scope="col">Status</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {(recentCases || []).map((item, key) => (<tr key={key}>
                                        <td>
                                            <Link to="#" className="fw-medium link-primary">{item.caseId}</Link>
                                        </td>
                                        <td>
                                            <div className="d-flex align-items-center">
                                                <div className="flex-shrink-0 me-2">
                                                    <img src={item.img} alt="" className="avatar-xs rounded-circle" />
                                                </div>
                                                <div className="flex-grow-1">{item.name}</div>
                                            </div>
                                        </td>
                                        <td>{item.doctor}</td>
                                        <td>{item.date}</td>
                                        <td>
                                            <span className={"badge bg-" + item.priorityClass+"-subtle text-"+item.priorityClass}>{item.priority}</span>
                                        </td>
                                        <td>
                                            <span className={"badge bg-" + item.statusClass+"-subtle text-"+item.statusClass}>{item.status}</span>
                                        </td>
                                    </tr>))}
                                </tbody>
                            </table>
                        </div>
                    </CardBody>
                </Card>
            </Col>
        </React.Fragment>
    );
};

export default RecentCases;
